"""T14B: isolated signal pilot; public weights/episodes/PPO, never a main-training initializer."""

from pathlib import Path
from typing import Any, cast
from dataclasses import replace
import faulthandler
import time
import sys
import gzip
import hashlib
import json
import math
import shutil

import torch

from .episode import emit
from .learning import EpisodeLearner, State, Transition
from .nanojev import NanoJevAdapter
from .schema import CandidateSet, EpisodeConfig, Goal, ModelConfig, Observation, PPOConfig
from .signal_diagnostics import critic_metrics, fixed_metrics, mc_returns, fixed_states, signal_gate, verdict, divergence, fit_critic
from .wood_pilot import attempt, evaluate, hashes, write_json
from .evaluation import reset_state
from .model_input import INPUT_HASH, choice_input
from .nanojev import REVISION, WEIGHTS_SHA256
from .rpc import EpisodeError


class SignalLearner(EpisodeLearner):
    def __init__(self, model: NanoJevAdapter, seed: int, directory: Path, validation: list[State]) -> None:
        super().__init__(model,PPOConfig(choice_lr=3e-4),seed,flush_on_finish=False,critic_warmup=8,pilot_signal=True)
        self.directory,self.validation=directory,validation
        self.history: list[Transition]=[]
        self.fixed_reports: list[dict[str,Any]]=[]
        self.warmup_reason: str | None=None
        with torch.no_grad():
            cast(torch.nn.Linear, cast(torch.nn.Sequential, model.critics["local"])[-1]).bias.zero_()

    def probe(self) -> None:
        report={"update":self.updates,"decisions":self.updates*128,"metrics":fixed_metrics(self.model,self.validation)}
        self.fixed_reports.append(report)
        write_json(self.directory/f"fixed-{self.updates:02d}.json",report)

    def update(self) -> None:
        if not self.rows:
            return
        offset=len(self.history)
        # History needs MC identities and critic inputs; full maps stay in the active rollout and fixed validation only.
        self.history.extend(replace(row,next_state=None,state=replace(row.state,observation=row.state.observation.model_copy(
            update={"observed_map":[]}))) for row in self.rows)
        warmup=self.config.critic_only
        targets=mc_returns(self.history)
        if warmup:
            fitting=[row for row,target in zip(self.history,targets) if target is not None]
            correct=[float(target) for target in targets if target is not None]
            self.ppo.config=self.config.model_copy(update={"epochs":32})
            report=self.ppo.update(fitting,mc_targets=correct)
        else:
            self.ppo.config=self.actor_config
            report=self.ppo.update(self.rows)
        current=[(row,float(target)) for row,target in zip(self.history[offset:],targets[offset:]) if target is not None]
        metrics=critic_metrics(self.model,[r for r,_ in current],[t for _,t in current])
        self.updates+=1
        if warmup and metrics["critic_ev"] is not None and metrics["critic_ev"]>=.3:
            self.warmup_reason="ev_threshold"
        elif warmup and self.updates>=8:
            self.warmup_reason="cap_reached"
        if self.warmup_reason:
            self.config=self.ppo.config=self.actor_config
        report.update(metrics,warmup=warmup,warmup_reason=self.warmup_reason,
                      cumulative_mc_samples=sum(t is not None for t in targets),rollout_transitions=len(self.rows))
        self.update_reports.append(report)
        emit("ppo_update",{"update":self.updates,**report})
        self.rows.clear()
        self.model.save_heads(self.directory/f"update-{self.updates:02d}.safetensors")
        self.probe()


def file_hash(path: Path) -> str:
    with path.open("rb") as handle:
        return hashlib.file_digest(handle,"sha256").hexdigest()


def initial_reference(reference: Path, expected: dict[str,Any], reason: str) -> tuple[dict[str,Any],dict[str,Any]]:
    """A fresh pilot actor may reuse a completed baseline; no optimizer/experience is resumed."""
    prior=json.loads((reference/"summary.json").read_text())
    prior_manifest=json.loads((reference/"manifest.json").read_text())
    signal=json.loads((reference/"signal-check.json").read_text())
    initial=[row for row in prior["evaluations"] if row["phase"]=="initial"]
    if (not reason.strip() or prior_manifest!=expected or prior.get("training") is not None
            or prior.get("error") is not None or not prior.get("restored_initial")
            or prior.get("stop_reason")!="initial_return_signal_not_demonstrated"
            or prior.get("signal")!=signal or signal.get("passed") is not False
            or prior.get("mock")!=(expected["config"]["backend"]=="mock")
            or prior.get("verdict")!="미판정" or list(reference.glob("update-*.safetensors"))
            or list(reference.glob("*train*.jsonl.gz"))):
        raise ValueError("Reference must be the unchanged, restored, untrained baseline with the same registered contract")
    missing=signal["by_kind"].get("mine_oak_log",{})
    others=[v for k,v in signal["by_kind"].items() if k!="mine_oak_log"]
    if (missing.get("bad_n")!=0 or missing.get("good_n",0)<=0 or missing.get("passed") is not False
            or missing.get("bad_mean") is not None or not others or not all(v["passed"] for v in others)):
        raise ValueError("User exception covers only missing bad samples in mine_oak_log; other signal checks must pass")
    if (len(initial)!=10 or [r["seed"] for r in initial]!=expected["evaluation_seeds"]
            or len({r["slot_id"] for r in initial})!=10
            or any(not r["attempts"] or not r["attempts"][-1]["valid"] for r in initial)
            or any(a.get("snapshot",expected["snapshot"])!=expected["snapshot"] for r in initial for a in r["attempts"])):
        raise ValueError("Reference requires all ten valid original initial slots and identical snapshot/seeds")
    evidence=[reference/name for name in ("summary.json","manifest.json","signal-check.json","fixed-states.jsonl.gz","initial.safetensors")]
    evidence += [Path(a["trace"]) for r in initial for a in r["attempts"]]
    receipt: dict[str,Any]={"reason":reason,"reference":str(reference),"original_gate_passed":False,
        "initial_signal_status":{"mine_oak_log":"not_assessable_missing_bad_samples"},
        "initial_evaluations":initial,"original_planned_slots":prior["planned_slots"],
        "original_unrun_post_slots":sum(not r["attempts"] for r in prior["evaluations"] if r["phase"]=="post"),
        "new_post_slots":10,"initial_evaluations_reused":10,"initial_evaluations_rerun":0}
    if expected["config"]["backend"]=="rpc":
        run=reference.parent.parent
        background=json.loads((run/"background-status.json").read_text())
        pin=json.loads((run/"run-manifest.json").read_text())
        if (background.get("status")!="failed" or background.get("phase")!="pilot" or background.get("native_crash")
                or not any(s["phase"]=="information" and s["returncode"]==0 for s in background["completed_stages"])):
            raise ValueError("Reference needs the completed information audit and gate-stopped pilot")
        allowed={"src/mc_diamond/signal_pilot.py","src/mc_diamond/cli.py"}
        changed=[name for name,digest in pin["sources"].items() if file_hash(Path(name))!=digest]
        if not pin["sources"] or set(changed)-allowed:
            raise ValueError("Safety/reward/model/candidate/runtime/snapshot inputs changed since the information audit")
        info=None
        with (run/"information.stdout").open() as handle:
            for line in handle:
                if line.startswith('{"type": "information_summary"'):
                    info=json.loads(line)["data"]
        certificate=run/"clock-verification-before.json"
        if (not info or not info["information_verified"] or info["hidden_hazard_peek"] or info["error"] is not None
                or file_hash(certificate)!=file_hash(Path("worlds/server/clock-verification.json"))):
            raise ValueError("Information audit or unchanged pause certificate is unavailable")
        evidence += [run/name for name in ("run-manifest.json","background-status.json","information.stdout","clock-verification-before.json")]
        receipt.update(information_audit_reused=True,information_audit_rerun=False,orchestration_source_changes=changed)
    else:
        receipt.update(information_audit_reused=False,information_audit_rerun=False,mock=True)
    receipt["files_sha256"]={str(p):file_hash(p) for p in evidence}
    return prior,receipt


def pilot_signal(config: EpisodeConfig, path: Path, output: Path,
                 reference: Path | None = None, exception_reason: str | None = None) -> int:
    started=time.monotonic()
    faulthandler.enable(file=2,all_threads=True)
    directory=output/("signal-user-exception" if reference else "signal")
    summary: dict[str,Any]={"mock":config.backend=="mock","planned_slots":10 if reference else 20,"evaluations":[],"training":None,
        "signal":None,"verdict":"미판정","probability_change":None,"restored_initial":False,"error":None,
        "main_training_decisions":0,"planner_calls":0,"api_cost_usd":0.}
    model: NanoJevAdapter | None=None
    initial: dict[str,str]={}
    snapshot="unavailable"
    reserved=False
    try:
        if (reference is None)!=(exception_reason is None) or exception_reason is not None and not exception_reason.strip():
            raise ValueError("Initial-evaluation reference and explicit user-exception reason must be supplied together")
        if not config.pilot_signal or config.ppo!=PPOConfig() or config.model and config.model.mode!="sampling":
            raise ValueError("pilot-signal requires T14B opt-in, default PPO and local sampling")
        if config.backend=="rpc" and (config.command is None or len(config.command)!=6
                or config.command[2:]!=["--task","G1","--budget-ticks","1800"]
                or Path(config.command[1]).resolve()!=Path("bridge/minecraft.js").resolve()):
            raise ValueError("Actual T14B pilot requires natural G1 with 1800 ticks")
        snapshot=reset_state(config,path,"G1")
        directory.mkdir(parents=True,exist_ok=False)
        reserved=True
        settings=config.model or ModelConfig()
        from .wood_pilot import EVALUATION_SEEDS
        manifest={"issue":51,"config":config.model_dump(mode="json"),"snapshot":snapshot,"training_seed":settings.seed,
            "evaluation_seeds":EVALUATION_SEEDS,"decisions":4096,"rollout":128,"updates":32,"choice_lr":3e-4,
            "warmup_ev":.3,"warmup_max_decisions":1024,"warmup_epochs":32,"critic_output_bias_zero":True,
            "warmup_target":"completed discounted MC return", "potential_D":32,"potential_k":.3/32,
            "moving_threshold":.10,"stationary_threshold":.03,"halfway_is_auxiliary":True,
            "input_hash":INPUT_HASH,"revision":REVISION,"weights_sha256":WEIGHTS_SHA256,
            "initial_success_gate":False,"main_training_initializer":False}
        previous: dict[str,Any]={}
        if reference is not None:
            reference=reference.resolve()
            previous,receipt=initial_reference(reference,manifest,cast(str,exception_reason))
            summary["user_exception"]=manifest["user_exception"]=receipt
        write_json(directory/"manifest.json",manifest)
        torch.manual_seed(settings.seed)
        model=NanoJevAdapter.load((path.parent/settings.checkpoint).resolve())
        initial=hashes(model)
        model.save_heads(directory/"initial.safetensors")
        if reference is not None:
            if initial!=previous["initial_hashes"]:
                raise ValueError("Fresh public actor/critics do not match the original baseline initial hashes")
            model.load_heads(reference/"initial.safetensors")
            if hashes(model)!=initial:
                raise ValueError("Referenced public initial heads differ from the fresh public model")
        summary["initial_hashes"]=initial
        initial_evaluations=summary["user_exception"]["initial_evaluations"] if reference else evaluate(config,path,directory,"initial",model,snapshot)
        if reference is None:
            summary["evaluations"]=initial_evaluations
        traces=[Path(r["attempts"][-1]["trace"]) for r in initial_evaluations if r["attempts"] and r["attempts"][-1]["valid"]]
        if reference is None:
            validation=fixed_states(model,traces,directory)
        else:
            validation=[]
            with gzip.open(reference/"fixed-states.jsonl.gz","rt") as handle:
                for line in handle:
                    row=json.loads(line)
                    observation,goal,saved=Observation.model_validate(row["observation"]),Goal.model_validate(row["goal"]),CandidateSet.model_validate(row["candidates"])
                    encoded=choice_input(observation,goal,saved)
                    features=model.encode_candidates(encoded)
                    validation.append(State(observation,goal,saved,features,torch.tensor(saved.mask,device=features.device),
                                            torch.tensor(encoded.context,device=features.device)))
            shutil.copyfile(reference/"fixed-states.jsonl.gz",directory/"fixed-states.jsonl.gz")
        summary["initial_fixed"]=fixed_metrics(model,validation)
        summary["signal"]=signal_gate(traces)
        if reference is not None:
            if summary["signal"]!=previous["signal"] or summary["initial_fixed"].keys()!=previous["initial_fixed"].keys():
                raise ValueError("Original signal/fixed-state contract changed")
            for kind,metrics in summary["initial_fixed"].items():
                for key,value in metrics.items():
                    original=previous["initial_fixed"][kind][key]
                    if value is None and original is not None or value is not None and (original is None or not math.isclose(value,original,abs_tol=1e-6,rel_tol=0)):
                        raise ValueError("Re-encoded original fixed states do not reproduce baseline metrics")
        write_json(directory/"signal-check.json",summary["signal"])
        if len(traces)!=10 or not validation or not summary["signal"]["passed"] and reference is None:
            summary["stop_reason"]="initial_return_signal_not_demonstrated"
        else:
            torch.manual_seed(settings.seed)
            learner=SignalLearner(model,settings.seed,directory,validation)
            learner.probe()
            episodes: list[dict[str,Any]]=[]
            collected=0
            errors: list[str]=[]
            while collected<4096:
                bounded=config.model_copy(update={"max_decisions":min(config.max_decisions,4096-collected)})
                row=attempt(bounded,path,directory,f"signal-train-{len(episodes)+1}",1,model,settings.seed,snapshot,learner)
                episodes.append(row); collected+=row["collected_decisions"]
                summary["training"]={"collected_decisions":collected,"updates":learner.update_reports,"episodes":episodes,
                    "actor_transitions":learner.actor_transitions,"valid_transitions":learner.valid_transitions,
                    "excluded_transitions":learner.excluded_transitions,"unupdated_transitions":len(learner.rows)+int(learner.pending is not None),
                    "warmup_reason":learner.warmup_reason,"errors":errors,"fixed_reports":learner.fixed_reports}
                write_json(directory/"summary.json",summary)
                if not row["valid"] or not row["collected_decisions"]:
                    errors.append(row["error_code"] or "no_progress")
                    break
            training=summary["training"]
            final=hashes(model)
            training.update(final_hashes=final,backbone_unchanged=final["backbone"]==initial["backbone"],
                choice_changed=final["choice"]!=initial["choice"],critic_changed=final["critics"]!=initial["critics"])
            usable=(collected==4096 and learner.updates==32 and not learner.rows and not errors
                    and training["backbone_unchanged"] and learner.actor_transitions>0)
            training["usable"]=usable
            summary["halfway"]=next((p for p in learner.fixed_reports if p["decisions"]==2048),None)
            if usable:
                first=summary["initial_fixed"]["all"]["good_probability"]
                last=learner.fixed_reports[-1]["metrics"]["all"]["good_probability"]
                summary["probability_change"]=last-first
                summary["verdict"]=verdict(last-first)
            summary["evaluations"].extend(evaluate(config,path,directory,"post",model,snapshot,
                unavailable=None if usable else "training_incomplete"))
            summary["critic_fit"]=fit_critic(model,learner.history,validation,traces)
            training_traces=[Path(r["trace"]) for r in episodes]
            summary["training_signal"]=signal_gate(training_traces)
            if reference is not None:
                summary["training_signal"]["initial_signal_status_unchanged"]=True
            summary["divergences"]=[{"seed":a["seed"],**divergence(Path(a["attempts"][-1]["trace"]),Path(b["attempts"][-1]["trace"]))}
                for a,b in zip(initial_evaluations,[r for r in summary["evaluations"] if r["phase"]=="post"])
                if a["attempts"] and b["attempts"] and a["attempts"][-1]["valid"] and b["attempts"][-1]["valid"]]
    except (ImportError,OSError,ValueError,RuntimeError,KeyError,TypeError,EpisodeError) as failure:
        summary["error"]=str(failure)
        print(f"pilot-signal failed: {failure}",file=sys.stderr)
    finally:
        if model is not None and (directory/"initial.safetensors").exists():
            try:
                model.load_heads(directory/"initial.safetensors")
                model.zero_grad(set_to_none=True); model.eval()
                summary["restored_initial"]=hashes(model)==initial
            except (OSError,ValueError,RuntimeError) as failure:
                summary["error"]=f"Initial head restoration failed: {failure}"
        summary["wall_seconds"]=time.monotonic()-started
        if "user_exception" in summary:
            try:
                unchanged=all(file_hash(Path(name))==digest for name,digest in summary["user_exception"]["files_sha256"].items())
            except OSError:
                unchanged=False
            summary["user_exception"]["reference_unchanged"]=unchanged
            if not unchanged:
                summary["error"]="Original reference evidence changed during continuation"
    if reserved:
        for phase in (("post",) if reference else ("initial","post")):
            if not any(row["phase"]==phase for row in summary["evaluations"]):
                summary["evaluations"].extend(evaluate(config,path,directory,phase,model,snapshot,unavailable="pilot_incomplete"))
        write_json(directory/"summary.json",summary)
    emit("pilot_signal_summary",summary)
    return 0 if summary["verdict"]!="미판정" and summary["restored_initial"] and not summary["error"] else 1
