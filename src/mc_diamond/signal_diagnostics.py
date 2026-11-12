"""T14B saved-state diagnostics. Labels use candidate text, never hidden state or action rewards."""

import gzip
import json
import math
import re
import statistics
from pathlib import Path
from typing import Any

import torch

from .learning import State, Transition, trace_masks
from .model_input import choice_input, text
from .nanojev import NanoJevAdapter
from .schema import CandidateSet, Goal, Observation


def mc_returns(rows: list[Transition]) -> list[float | None]:
    masks = trace_masks(rows)
    targets: list[float | None] = [None] * len(rows)
    for i in range(len(rows)-1, -1, -1):
        row = rows[i]
        if row.valid and not row.bootstrap:
            targets[i] = row.reward
        elif masks[i] and i+1 < len(rows):
            following = targets[i+1]
            if following is not None:
                targets[i] = row.reward + row.discount * following
    return targets


def critic_metrics(model: NanoJevAdapter, rows: list[Transition], targets: list[float]) -> dict[str, Any]:
    with torch.no_grad():
        predictions = [float(model.score_features(r.state.features, r.state.mask, r.state.context)[1]["local"]) for r in rows]
    variance = statistics.pvariance(targets) if targets else 0.
    return {"mc_samples": len(targets), "critic_ev": 1-statistics.pvariance(
            [a-b for a,b in zip(targets,predictions)])/variance if variance>0 else None,
        "prediction_mean": statistics.mean(predictions) if predictions else None,
        "return_mean": statistics.mean(targets) if targets else None}


def classify(goal: Goal, saved: CandidateSet) -> tuple[str, list[bool]] | None:
    allowed = [c for c,m in zip(saved.candidates,saved.mask) if m]
    if len(allowed)<2 or goal.kind != "collect":
        return None
    if all(c.action_kind == "move_observed" and ":move:" in c.candidate_id for c in allowed):
        source = "stone" if goal.target=="cobblestone" else goal.target
        good = [bool(re.search(r"(?:: |, )"+re.escape(source)+r" \d+", c.description or "")) and m
                for c,m in zip(saved.candidates,saved.mask)]
        if any(good) and sum(good)<len(allowed):
            return "move_"+source,good
    if {c.action_kind for c in allowed}=={"mine_visible_cluster","move_observed"}:
        return "mine_"+goal.target,[m and c.action_kind=="mine_visible_cluster" for c,m in zip(saved.candidates,saved.mask)]
    return None


def position_key(observation: Observation) -> str:
    return text([observation.position,sorted(observation.inventory.items())])


def state_key(observation: Observation, goal: Goal, saved: CandidateSet) -> str:
    return text(choice_input(observation,goal,saved).payload)


def decisions(trace: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]]=[]
    current: dict[str, Any]={}
    with gzip.open(trace,"rt",encoding="utf-8") as handle:
        for line in handle:
            row=json.loads(line); kind,data=row["type"],row["data"]
            if kind=="observation":
                current={"observation":data}
            elif kind in {"goal","candidates","selection","step"}:
                current[kind]=data
            elif kind=="reward":
                current["reward"]=data
                current["valid"]=not current["step"]["invalid"] and (
                    current["step"]["stable_boundary"] or data.get("task_terminal",False))
                rows.append(current)
    # Only complete, reliable return segments are targets; do not turn an operational tail into a terminal.
    total: float | None=None
    for row in reversed(rows):
        reward=row["reward"]
        if not row["valid"]:
            total=None
        elif reward.get("task_terminal",False):
            total=reward["discounted"]
        elif total is not None and not row["step"]["cancelled"]:
            total=reward["discounted"]+reward["discount"]*total
        else:
            total=None
        row["mc_return"]=total
        if row["step"]["cancelled"]:
            total=None
    return rows


def fixed_states(model: NanoJevAdapter, traces: list[Path], directory: Path) -> list[State]:
    unique: dict[str,State]={}
    sources=[]
    for trace in traces:
        for index,row in enumerate(decisions(trace)):
            observation=Observation.model_validate(row["observation"])
            goal=Goal.model_validate(row["goal"]); saved=CandidateSet.model_validate(row["candidates"])
            if not row["valid"] or row["step"]["cancelled"] or classify(goal,saved) is None:
                continue
            key=state_key(observation,goal,saved)
            if key in unique:
                continue
            encoded=choice_input(observation,goal,saved)
            features=model.encode_candidates(encoded)
            unique[key]=State(observation,goal,saved,features,torch.tensor(saved.mask,device=features.device),
                              torch.tensor(encoded.context,device=features.device))
            sources.append({"trace":str(trace),"index":index,"observation":row["observation"],
                            "goal":row["goal"],"candidates":row["candidates"]})
    with (directory/"fixed-states.jsonl.gz").open("xb") as raw:
        with gzip.open(raw,"wt",encoding="utf-8") as handle:
            for row in sources:
                handle.write(text(row)+"\n")
    return list(unique.values())


def fixed_metrics(model: NanoJevAdapter, states: list[State]) -> dict[str, Any]:
    groups: dict[str,list[dict[str,float]]]={"all":[]}
    training=model.training
    model.eval()
    try:
        with torch.no_grad():
            for state in states:
                found=classify(state.goal,state.candidates)
                assert found is not None
                kind,good=found
                logits,_=model.score_features(state.features,state.mask,state.context)
                probabilities=logits.softmax(-1)
                positive=probabilities[state.mask]
                row={"good_probability":float(probabilities[torch.tensor(good,device=logits.device)].sum()),
                     "uniform_share":sum(good)/int(state.mask.sum()),
                     "normalized_entropy":float(-(positive*positive.clamp_min(1e-30).log()).sum())/math.log(len(positive))}
                groups.setdefault(kind,[]).append(row); groups["all"].append(row)
    finally:
        model.train(training)
    return {kind:{"states":len(rows),**{k:statistics.mean(r[k] for r in rows) if rows else None
              for k in ("good_probability","uniform_share","normalized_entropy")}} for kind,rows in groups.items()}


def signal_gate(traces: list[Path]) -> dict[str, Any]:
    groups: dict[str,dict[str,list[float]]]={}
    completions: dict[str,int]={"oak_log":0,"wooden_pickaxe":0,"cobblestone":0}
    first: dict[str,int]={}
    for trace in traces:
        rows=decisions(trace)
        if rows:
            selected=rows[0]["selection"]["candidate_id"].split(":",1)[-1]
            first[selected]=first.get(selected,0)+1
        seen=set()
        for row in rows:
            goal=Goal.model_validate(row["goal"])
            if row["reward"].get("task_terminal") and row["step"]["observation"]["remaining_ticks"]>0 and row["step"]["observation"]["health"]>0:
                seen.add(goal.target)
            found=classify(goal,CandidateSet.model_validate(row["candidates"]))
            if found is None:
                continue
            kind,good=found
            groups.setdefault(kind,{"good":[],"bad":[]})
            if row["mc_return"] is None or row["step"]["cancelled"]:
                continue
            ids=[c["candidate_id"] for c in row["candidates"]["candidates"]]
            selected=row["selection"]["candidate_id"]
            if selected in ids:
                groups.setdefault(kind,{"good":[],"bad":[]})["good" if good[ids.index(selected)] else "bad"].append(row["mc_return"])
        for target in seen:
            completions[target]=completions.get(target,0)+1
    result={kind:{"good_n":len(g["good"]),"bad_n":len(g["bad"]),
        "good_mean":statistics.mean(g["good"]) if g["good"] else None,
        "bad_mean":statistics.mean(g["bad"]) if g["bad"] else None,
        "passed":bool(g["good"] and g["bad"] and statistics.mean(g["good"])>statistics.mean(g["bad"]))}
        for kind,g in groups.items()}
    return {"passed":bool(result) and all(g["passed"] for g in result.values()),"by_kind":result,
            "completion_counts":completions,"episodes":len(traces),"first_selection_counts":first}


def verdict(change: float | None) -> str:
    return "미판정" if change is None else "움직임" if change>=.10 else "움직이지 않음" if change<.03 else "판정 보류"


def divergence(before: Path, after: Path) -> dict[str, Any]:
    left,right=decisions(before),decisions(after)
    for i,(a,b) in enumerate(zip(left,right)):
        x,y=a["observation"],b["observation"]
        if x["inventory"]!=y["inventory"]:
            return {"decision":i,"cause":"drop_timing","evidence":"inventory differs before selection"}
        if x["observed_map"]!=y["observed_map"]:
            return {"decision":i,"cause":"map_difference"}
        oa,ob=Observation.model_validate(x),Observation.model_validate(y)
        ga,gb=Goal.model_validate(a["goal"]),Goal.model_validate(b["goal"])
        ca,cb=CandidateSet.model_validate(a["candidates"]),CandidateSet.model_validate(b["candidates"])
        if ca.candidates and cb.candidates and state_key(oa,ga,ca)==state_key(ob,gb,cb):
            ia=next((j for j,c in enumerate(ca.candidates) if c.candidate_id==a["selection"]["candidate_id"]),None)
            ib=next((j for j,c in enumerate(cb.candidates) if c.candidate_id==b["selection"]["candidate_id"]),None)
            if ia!=ib:
                return {"decision":i,"cause":"policy"}
        elif x!=y or a["goal"]!=b["goal"] or a["candidates"]!=b["candidates"]:
            # Identities alone are deliberately excluded from the policy-state key.
            from .information import policy_signature
            if policy_signature({"state":x,"goal":a["goal"],"candidates":a["candidates"]}) != policy_signature(
                    {"state":y,"goal":b["goal"],"candidates":b["candidates"]}):
                return {"decision":i,"cause":"other_state_or_candidates"}
    return {"decision":min(len(left),len(right)),"cause":"identical" if len(left)==len(right) else "length_difference"}


def fit_critic(model: NanoJevAdapter, history: list[Transition], validation: list[State], traces: list[Path]) -> dict[str, Any]:
    from copy import deepcopy

    targets=mc_returns(history)
    excluded={position_key(state.observation) for state in validation}
    training=[(row.state,float(target)) for row,target in zip(history,targets)
              if target is not None and position_key(row.state.observation) not in excluded]
    lookup={}
    for trace in traces:
        for row in decisions(trace):
            if row["mc_return"] is not None and row["candidates"]["candidates"]:
                lookup[state_key(Observation.model_validate(row["observation"]),Goal.model_validate(row["goal"]),
                                 CandidateSet.model_validate(row["candidates"]))]=row["mc_return"]
    testing=[(s,lookup[state_key(s.observation,s.goal,s.candidates)]) for s in validation
             if state_key(s.observation,s.goal,s.candidates) in lookup]
    report: dict[str,Any]={"training_states":len(training),"validation_states":len(testing),
                          "steps":[],"split":"initial-eval validation; exclude its position/inventory from training"}
    if not training or not testing:
        return {**report,"not_run_reason":"no_disjoint_complete_mc_samples"}
    device=next(model.parameters()).device
    def tensors(rows: list[tuple[State,float]]) -> tuple[torch.Tensor,torch.Tensor]:
        return (torch.stack([torch.cat([s.features[s.mask].float().mean(0),s.context.float()]) for s,_ in rows]),
                torch.tensor([value for _,value in rows],device=device))
    train_x,train_y=tensors(training); test_x,test_y=tensors(testing)
    with torch.random.fork_rng(devices=[device.index or 0] if device.type=="cuda" else []):
        torch.manual_seed(11051)
        head=deepcopy(model.critics["local"])
        for module in head.modules():
            if isinstance(module,torch.nn.Linear):
                module.reset_parameters()
        optimizer=torch.optim.Adam(head.parameters(),lr=1e-4)
        for i in range(1,2001):
            batch=torch.randint(len(training),(min(32,len(training)),),device=device)
            loss=(head(train_x[batch]).squeeze(-1)-train_y[batch]).square().mean()
            if not torch.isfinite(loss):
                raise ValueError("Nonfinite auxiliary critic loss")
            optimizer.zero_grad(); loss.backward(); optimizer.step()
            if i in (128,2000):
                with torch.no_grad():
                    prediction=head(test_x).squeeze(-1)
                    variance=test_y.var(unbiased=False)
                    ev=float(1-(prediction-test_y).var(unbiased=False)/variance) if variance>0 else None
                report["steps"].append({"step":i,"validation_ev":ev,"prediction_mean":float(prediction.mean()),
                                        "return_mean":float(test_y.mean())})
    return report
