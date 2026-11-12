"""T14B opt-in contracts; tiny numerical checks and public CLI with a scripted game."""

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest
import yaml
from dataclasses import replace

from mc_diamond.rewards import RewardLedger
from mc_diamond.schema import Goal, Surface
from test_learning import event, observation, step


def test_direct_collect_pays_each_unit_once_without_completion_bonus_or_given_stock() -> None:
    before = observation(remaining_ticks=1800, inventory={"oak_log": 1})
    goal = Goal(goal_id="logs", kind="collect", target="oak_log", quantity=3)
    ledger = RewardLedger(before, pilot_signal=True)
    values = []
    for i in range(3):
        acquired = event("acquired", "oak_log", event_id=f"e{i}")
        result = ledger.compute(before, goal, step(before, events=[acquired]), goal_completed=i >= 1)
        values.append(result.components.get("collect", 0.))
        assert "success" not in result.components
    assert values == pytest.approx([1/3, 1/3, 0.])  # one unit was provided; only two are payable
    duplicate = ledger.compute(before, goal, step(before, events=[acquired]), goal_completed=True)
    assert duplicate.components.get("collect", 0.) == 0.
    empty = observation(remaining_ticks=1800)
    paid = RewardLedger(empty, pilot_signal=True).compute(empty, goal,
        step(empty, events=[event("acquired", "oak_log", quantity=9)]), goal_completed=True)
    assert paid.components["collect"] == 1.
    default = RewardLedger(empty).compute(empty, goal, step(empty), goal_completed=False)
    assert default.components == {"time": pytest.approx(-.1/90)}


def test_visible_potential_telescopes_and_target_removal_with_one_unit_is_nonnegative() -> None:
    goal = Goal(goal_id="stone", kind="collect", target="cobblestone", quantity=3)
    start = observation(remaining_ticks=1800, position=[0., 64., 0.], observed_map=[
        Surface(block="stone", position=[10., 64., 0.]),
        Surface(block="stone", position=[0., 64., 0.], visible=False)])
    ledger = RewardLedger(start, pilot_signal=True)
    middle = start.model_copy(update={"position": [5., 64., 0.], "active_ticks": 100, "remaining_ticks": 1700})
    end = middle.model_copy(update={"observed_map": [], "active_ticks": 500, "remaining_ticks": 1300})
    first = ledger.compute(start, goal, step(start, 100, observation=middle), goal_completed=False)
    last = ledger.compute(middle, goal, step(middle, 400, observation=end,
        events=[event("acquired", "cobblestone")]), goal_completed=False)
    assert first.components["approach"] > 0
    assert last.components["approach"] < 0
    assert last.discounted > 0  # even at the maximum macro length, the acquired third outweighs removal
    assert first.components["approach"] + first.discount*last.components["approach"] == pytest.approx(
        .09375 - 2**(-500/1800)*.3)
    terminal = ledger.compute(middle, goal, step(middle, 100, observation=end), goal_completed=True)
    assert terminal.terminal and terminal.components["approach"] == pytest.approx(.046875)
    craft = Goal(goal_id="pick", kind="craft", target="wooden_pickaxe", quantity=1)
    assert RewardLedger(start, pilot_signal=True).compute(start, craft, step(start),
        goal_completed=False).components.get("approach", 0.) == 0.
    full = observation(objective_kind="full", remaining_ticks=1800)
    assert RewardLedger(full, pilot_signal=True).compute(full, goal, step(full),
        goal_completed=False).components == {"time": -.001}


def chain_fixture() -> dict[str, Any]:
    template = json.loads(Path("fixtures/model_episode.json").read_text())
    initial = {**template["initial"], "remaining_ticks": 1800}
    steps = []
    inventories = [{"oak_log": 3}, {"wooden_pickaxe": 1}, {"wooden_pickaxe": 1, "cobblestone": 3}]
    for i, inventory in enumerate(inventories, 1):
        item = ["oak_log", "wooden_pickaxe", "cobblestone"][i-1]
        now = {**initial, "obs_id": f"obs-{i}", "active_ticks": 20*i, "remaining_ticks": 1800-20*i,
            "inventory": inventory, "tool": "wooden_pickaxe" if i>1 else None,
            "observed_map": [{"block": "stone", "position": [1., 64., 0.]}] if i>1 else initial["observed_map"]}
        result = {**template["steps"][0], "observation": now, "terminated": i==3,
            "reason": "macro_completed", "source_obs_id": f"obs-{i-1}",
            "stop_evidence": [f"obs-{i}", "macro_completed"],
            "events": [{"kind": "crafted" if i==2 else "acquired", "item": item,
                        "quantity": 1 if i==2 else 3, "event_id": f"event{i}", "source": "mock"}]}
        steps.append(result)
    return {"initial": initial, "steps": steps}


def test_public_chain_continues_same_state_and_pays_three_local_boundaries(tmp_path: Path) -> None:
    fixture = tmp_path/"chain.json"
    fixture.write_text(json.dumps(chain_fixture()))
    config = tmp_path/"chain.yaml"
    config.write_text(yaml.safe_dump({"backend":"mock", "fixture": str(fixture), "pilot_signal":True,
        "max_decisions":10, "goal":{"goal_id":"pilot", "kind":"collect", "target":"cobblestone", "quantity":3}}))
    run = subprocess.run(["mc-diamond", "smoke-macros", "--config", str(config)],
                         capture_output=True, text=True, timeout=15)
    assert run.returncode==0, run.stderr
    rows=[json.loads(line) for line in run.stdout.splitlines()]
    assert sum(row["type"]=="reset" for row in rows)==1
    assert [row["data"]["target"] for row in rows if row["type"]=="goal"] == ["oak_log","wooden_pickaxe","cobblestone"]
    rewards=[row["data"] for row in rows if row["type"]=="reward"]
    assert [r["task_terminal"] for r in rewards]==[True,True,True]
    assert sum(r["components"].get("collect",0.)+r["components"].get("success",0.) for r in rewards)==3.
    assert rows[-1]["data"]["goal_completed"] and rows[-1]["data"]["decisions"]==3


def test_mc_targets_stop_at_subgoals_and_wait_for_a_completed_tail() -> None:
    from mc_diamond.signal_diagnostics import mc_returns
    from test_learning import transition
    first=transition()
    following=replace(first, state=replace(first.state,
        observation=first.state.observation.model_copy(update={"obs_id":"obs-next"}),
        candidates=first.state.candidates.model_copy(update={"candidates":[c.model_copy(update={"source_obs_id":"obs-next"})
                                                                        for c in first.state.candidates.candidates]})),
        reward=2., bootstrap=False, next_obs_id="end")
    assert mc_returns([first]) == [None]
    assert mc_returns([first,following]) == [2.,2.]  # 1 + .5*2, terminal2
    assert mc_returns([replace(first,bootstrap=False),following]) == [1.,2.]
    assert mc_returns([first,replace(following,trace_break=True)]) == [None,2.]
    assert mc_returns([first,replace(following,valid=False,actor_valid=False)]) == [None,None]


def test_explicit_critic_targets_ignore_bootstrapped_value_and_leave_choice_unchanged() -> None:
    from mc_diamond.learning import PPO
    from mc_diamond.nanojev import parameter_hash
    from mc_diamond.schema import PPOConfig
    from test_learning import transition
    from test_model import tiny_adapter
    model=tiny_adapter()
    original=parameter_hash(model.choice)
    report=PPO(model,PPOConfig(critic_only=True,epochs=1)).update([transition()],mc_targets=[.125])
    assert report["returns"] == [.125]
    assert parameter_hash(model.choice)==original and report["actor_skipped"]
    with pytest.raises(ValueError):
        PPO(model,PPOConfig()).update([transition()],mc_targets=[float("nan")])


def test_warmup_uses_cumulative_completed_mc_and_stops_at_eight_rollouts(tmp_path: Path) -> None:
    from mc_diamond.signal_pilot import SignalLearner
    from mc_diamond.nanojev import parameter_hash
    from test_learning import transition
    from test_model import tiny_adapter
    model=tiny_adapter()
    learner=SignalLearner(model,11,tmp_path,[])
    choice=parameter_hash(model.choice)
    assert model.critics["local"][-1].bias.item()==0.
    row=replace(transition(),bootstrap=False,actor_valid=False)
    for i in range(8):
        learner.rows=[row]
        learner.update()
        report=learner.update_reports[-1]
        assert report["warmup"] and report["cumulative_mc_samples"]==i+1 and report["mc_samples"]==1
        assert report["returns"]==[1.]*(i+1)
        assert parameter_hash(model.choice)==choice
    assert learner.warmup_reason=="cap_reached" and not learner.config.critic_only
    assert len(list(tmp_path.glob("update-*.safetensors")))==8


def test_signal_history_drops_observed_maps_but_keeps_mc_and_critic_inputs(tmp_path: Path) -> None:
    """Cumulative diagnostics must not retain full maps from all 4,096 decisions."""
    from mc_diamond.signal_diagnostics import mc_returns, position_key
    from mc_diamond.signal_pilot import SignalLearner
    from test_learning import transition
    from test_model import tiny_adapter
    learner=SignalLearner(tiny_adapter(),11,tmp_path,[])
    row=replace(transition(),bootstrap=False,actor_valid=False)
    assert row.state.observation.observed_map
    learner.rows=[row]
    learner.update()
    kept=learner.history[0]
    assert not kept.state.observation.observed_map and kept.next_state is None
    assert position_key(kept.state.observation)==position_key(row.state.observation)
    assert mc_returns(learner.history)==mc_returns([row]) and bool((kept.state.features==row.state.features).all())


def test_warmup_can_end_at_ev_threshold_and_never_labels_unfinished_mc(tmp_path: Path) -> None:
    import torch
    from mc_diamond.signal_pilot import SignalLearner
    from test_learning import transition
    from test_model import tiny_adapter
    model=tiny_adapter()
    learner=SignalLearner(model,11,tmp_path,[])
    first=transition()
    second=replace(first,state=replace(first.state,features=first.state.features*2))
    with torch.no_grad():
        rows=[replace(r,reward=float(model.score_features(r.state.features,r.state.mask,r.state.context)[1]["local"]),
                      bootstrap=False,actor_valid=False) for r in [first,second]]
    learner.rows=rows
    learner.update()
    assert learner.warmup_reason=="ev_threshold" and learner.updates==1 and not learner.config.critic_only
    assert learner.update_reports[0]["critic_ev"] == pytest.approx(1.,abs=.01)


def test_goal_specific_labels_masks_and_registered_thresholds() -> None:
    from mc_diamond.signal_diagnostics import classify, verdict
    from mc_diamond.schema import Candidate, CandidateSet
    candidates=[Candidate(candidate_id=f"o:move:{i}",action_kind="move_observed",params={},max_ticks=20,
        source_obs_id="o",stop_rule_id="path",description=desc) for i,desc in enumerate([
            "visible: oak_log 2", "visible: stone 3", "visible: oak_log 1, stone 1"])]
    saved=CandidateSet(candidates=candidates,mask=[True,True,False],generated=3)
    wood=Goal(goal_id="wood",kind="collect",target="oak_log",quantity=3)
    stone=wood.model_copy(update={"target":"cobblestone"})
    assert classify(wood,saved)==("move_oak_log",[True,False,False])
    assert classify(stone,saved)==("move_stone",[False,True,False])
    assert classify(wood.model_copy(update={"kind":"craft"}),saved) is None
    assert [verdict(v) for v in [None,0.,.029999,.03,.099999,.10]]==[
        "미판정","움직이지 않음","움직이지 않음","판정 보류","판정 보류","움직임"]


def test_signal_gate_rejects_missing_or_nonpositive_good_choice_advantage(tmp_path: Path) -> None:
    import gzip
    from mc_diamond.signal_diagnostics import signal_gate
    assert not signal_gate([])["passed"]
    trace=tmp_path/"trace.jsonl.gz"
    wood=Goal(goal_id="wood",kind="collect",target="oak_log",quantity=3).model_dump()
    candidates={"candidates":[{"candidate_id":f"obs-0:move:{i}","action_kind":"move_observed","params":{},
        "max_ticks":20,"source_obs_id":"obs-0","stop_rule_id":"path","description":d}
        for i,d in enumerate(["visible: oak_log 2","visible: stone 1"])],"mask":[True,True],"generated":2}
    def write(value: float, chosen: int) -> None:
        rows=[("observation",observation().model_dump()),("goal",wood),("candidates",candidates),
            ("selection",{"candidate_id":f"obs-0:move:{chosen}"}),
            ("step",step(observation()).model_dump()),
            ("reward",{"discounted":value,"discount":.9,"task_terminal":True})]
        with gzip.open(trace,"wt") as handle:
            for kind,data in rows:
                handle.write(json.dumps({"type":kind,"data":data})+"\n")
    write(1.,0)
    assert not signal_gate([trace])["passed"]  # no bad choices, no invented comparison
    other=tmp_path/"other.gz"
    other.write_bytes(trace.read_bytes())
    write(1.,1)
    assert not signal_gate([trace,other])["passed"]
    write(.25,1)
    assert signal_gate([trace,other])["passed"]


def test_trace_mc_diagnostics_do_not_cross_local_subgoal_terminals(tmp_path: Path) -> None:
    import gzip
    from mc_diamond.pilot_diagnostics import trace_diagnostics
    trace=tmp_path/"returns.gz"
    with gzip.open(trace,"wt") as handle:
        for reward,bootstrap in [(.2,True),(.8,False),(1.,False),(.4,True)]:
            handle.write(json.dumps({"type":"transition","data":{"reward":reward,"discount":.5,
                "old_value":0.,"valid":True,"bootstrap":bootstrap}})+"\n")
    result=trace_diagnostics(trace,0.)
    assert result["mc_returns"] == pytest.approx([.6,.8,1.])


def test_signal_cli_stops_before_learning_when_signal_is_missing_and_restores_all_heads(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    import sys
    import torch
    from mc_diamond.cli import main
    from mc_diamond.nanojev import NanoJevAdapter, parameter_hash
    from test_model import tiny_adapter
    torch.set_num_threads(1)
    model=tiny_adapter()
    class Tokenizer:
        eos_token_id=1
        pad_token_id=0
        def encode(self,value: str,add_special_tokens: bool) -> list[int]:
            return [ord(c)%128 for c in value]
    model.tokenizer=Tokenizer()
    original=parameter_hash(model)
    monkeypatch.setattr(NanoJevAdapter,"load",classmethod(lambda cls,root:model))
    fixture=tmp_path/"chain.json"; fixture.write_text(json.dumps(chain_fixture()))
    config=tmp_path/"chain.yaml"
    config.write_text(yaml.safe_dump({"backend":"mock","fixture":str(fixture),"pilot_signal":True,
        "goal":{"goal_id":"pilot","kind":"collect","target":"cobblestone","quantity":3},"max_decisions":30}))
    monkeypatch.setattr(sys,"argv",["mc-diamond","pilot-signal","--config",str(config),"--output",str(tmp_path/"pilot")])
    assert main()==1
    summary=json.loads(capsys.readouterr().out.splitlines()[-1])["data"]
    assert summary["mock"] and summary["training"] is None and summary["restored_initial"]
    assert summary["verdict"]=="미판정" and summary["planned_slots"]==20 and len(summary["evaluations"])==20
    assert sum(bool(r["attempts"]) for r in summary["evaluations"])==10
    assert summary["stop_reason"]=="initial_return_signal_not_demonstrated"
    assert parameter_hash(model)==original
    saved=(tmp_path/"pilot/signal/summary.json").read_bytes()
    assert main()==1
    assert (tmp_path/"pilot/signal/summary.json").read_bytes()==saved


def test_auxiliary_critic_fit_excludes_validation_positions_and_preserves_live_model_and_rng(tmp_path: Path) -> None:
    import gzip
    import torch
    from mc_diamond.signal_diagnostics import fit_critic
    from mc_diamond.nanojev import parameter_hash
    from test_learning import transition
    from test_model import tiny_adapter
    torch.set_num_threads(1)
    model=tiny_adapter()
    source=transition()
    states=[replace(source.state,observation=source.state.observation.model_copy(update={"position":[float(i),64.,0.]}),
                    features=source.state.features*float(i+1)) for i in range(4)]
    trace=tmp_path/"validation.gz"
    with gzip.open(trace,"wt") as handle:
        for state,target in zip(states[:2],[.1,.9]):
            rows=[("observation",state.observation.model_dump()),("goal",state.goal.model_dump()),
                  ("candidates",state.candidates.model_dump()),("selection",{"candidate_id":"saved-0"}),
                  ("step",step(state.observation).model_dump()),
                  ("reward",{"discounted":target,"discount":.9,"task_terminal":True})]
            for kind,data in rows:
                handle.write(json.dumps({"type":kind,"data":data})+"\n")
    history=[replace(source,state=s,reward=r,bootstrap=False) for s,r in zip(states,[.1,.9,.2,.8])]
    before=parameter_hash(model); rng=torch.get_rng_state().clone()
    result=fit_critic(model,history,states[:2],[trace])
    assert result["training_states"]==2 and result["validation_states"]==2
    assert [r["step"] for r in result["steps"]]==[128,2000]
    assert all(r["validation_ev"] is not None for r in result["steps"])
    assert parameter_hash(model)==before and torch.equal(rng,torch.get_rng_state())
    assert fit_critic(model,history[:2],states[:2],[trace])["not_run_reason"]=="no_disjoint_complete_mc_samples"


def test_learning_chain_records_a_terminal_for_every_subgoal_without_resetting(
        tmp_path: Path,monkeypatch: pytest.MonkeyPatch,capsys: pytest.CaptureFixture[str]) -> None:
    import sys
    from mc_diamond.cli import main
    from mc_diamond.nanojev import NanoJevAdapter
    from test_model import tiny_adapter
    model=tiny_adapter()
    class Tokenizer:
        eos_token_id=1
        pad_token_id=0
        def encode(self,value: str,add_special_tokens: bool) -> list[int]:
            return [ord(c)%128 for c in value]
    model.tokenizer=Tokenizer()
    monkeypatch.setattr(NanoJevAdapter,"load",classmethod(lambda cls,root:model))
    fixture=tmp_path/"chain.json"; fixture.write_text(json.dumps(chain_fixture()))
    config=tmp_path/"chain.yaml"
    config.write_text(yaml.safe_dump({"backend":"mock","fixture":str(fixture),"pilot_signal":True,
        "goal":{"goal_id":"pilot","kind":"collect","target":"cobblestone","quantity":3},"max_decisions":30}))
    monkeypatch.setattr(sys,"argv",["mc-diamond","smoke-ppo","--config",str(config)])
    assert main()==0
    output=[json.loads(line) for line in capsys.readouterr().out.splitlines()]
    rows=[r["data"] for r in output if r["type"]=="transition"]
    assert len(rows)==3 and all(not r["bootstrap"] for r in rows)
    assert sum(r["type"]=="reset" for r in output)==1


@pytest.mark.parametrize(("reuse_initial","fail_after_update"),[(False,False),(False,True),(True,False),(True,True)],
                         ids=["ordinary","ordinary-fault","reference","reference-fault"])
def test_full_signal_cli_preserves_4096_decisions_32_updates_and_20_slots(
        tmp_path: Path,monkeypatch: pytest.MonkeyPatch,capsys: pytest.CaptureFixture[str],fail_after_update: bool,
        reuse_initial: bool) -> None:
    """Scripted initial evaluation traces supply a positive gate; training/post use real public mock RPC/PPO."""
    import gzip
    import sys
    import torch
    from mc_diamond.cli import main
    from mc_diamond.nanojev import NanoJevAdapter, parameter_hash
    from mc_diamond import signal_pilot
    from test_model import tiny_adapter
    torch.set_num_threads(1)
    model=tiny_adapter()
    class Tokenizer:
        eos_token_id=1
        pad_token_id=0
        def encode(self,value: str,add_special_tokens: bool) -> list[int]:
            return [ord(c)%128 for c in value]
    model.tokenizer=Tokenizer()
    original=parameter_hash(model)
    monkeypatch.setattr(NanoJevAdapter,"load",classmethod(lambda cls,root:model))
    if fail_after_update:
        real_update=signal_pilot.SignalLearner.update
        def failing_update(learner: Any) -> None:
            real_update(learner)
            if learner.updates:
                raise RuntimeError("Injected failure after a real critic update")
        monkeypatch.setattr(signal_pilot.SignalLearner,"update",failing_update)
    from mc_diamond.wood_pilot import evaluate as original_evaluate
    def evaluate(config: Any,path: Path,directory: Path,phase: str,loaded: Any,snapshot: str,**kwargs: Any) -> Any:
        if phase!="initial":
            return original_evaluate(config,path,directory,phase,loaded,snapshot,**kwargs)
        slots=[]
        for i in range(10):
            trace=directory/f"initial-eval-{i+1}-1.jsonl.gz"
            initial=chain_fixture()["initial"]
            goal=Goal(goal_id="pilot:logs",kind="collect",target="oak_log",quantity=3)
            candidates={"candidates":[{"candidate_id":f"obs-0:move:{j}","action_kind":"move_observed","params":{},
                "max_ticks":20,"source_obs_id":"obs-0","stop_rule_id":"path","description":desc}
                for j,desc in enumerate(["visible: oak_log 2","visible: stone 1"])],"mask":[True,True],"generated":2}
            rows=[("observation",initial),("goal",goal.model_dump()),("candidates",candidates),
                ("selection",{"candidate_id":f"obs-0:move:{i%2}"}),
                ("step",step(observation(remaining_ticks=1800)).model_dump()),
                ("reward",{"discounted":1. if i%2==0 else 0.,"discount":.9,"task_terminal":True})]
            if reuse_initial:
                mine=json.loads(json.dumps(candidates))
                mine["candidates"][0].update(action_kind="mine_visible_cluster",description="Mine exposed oak_log")
                mine["candidates"][1].update(description="Approach exposed oak_log")
                rows += [(kind,mine if kind=="candidates" else {"candidate_id":"obs-0:move:0"} if kind=="selection"
                          else {"discounted":.5,"discount":.9,"task_terminal":True} if kind=="reward" else data)
                         for kind,data in rows[:]]
            with gzip.open(trace,"wt") as handle:
                for kind,data in rows:
                    handle.write(json.dumps({"type":kind,"data":data})+"\n")
            slots.append({"slot_id":f"initial-eval-{i+1}","phase":"initial","seed":15000+i,"success":True,
                          "attempts":[{"trace":str(trace),"valid":True}],"not_run_reason":None})
        return slots
    monkeypatch.setattr(signal_pilot,"evaluate",evaluate)
    data=chain_fixture()
    first,craft,last=data["steps"]
    data["steps"]=[]
    for i in range(1,33):
        template=first if i==1 else craft if i==2 else last
        result=json.loads(json.dumps(template))
        result.update(source_obs_id=f"obs-{i-1}",terminated=i==32,stop_evidence=[f"obs-{i}","macro_completed"])
        result["observation"].update(obs_id=f"obs-{i}",active_ticks=i*20,remaining_ticks=1800-i*20)
        if 2<i<32:
            result["events"]=[{"kind":"stopped","source":"mock"}]
            result["observation"]["inventory"]={"wooden_pickaxe":1}
        data["steps"].append(result)
    fixture=tmp_path/"chain.json"; fixture.write_text(json.dumps(data))
    config=tmp_path/"chain.yaml"
    config.write_text(yaml.safe_dump({"backend":"mock","fixture":str(fixture),"pilot_signal":True,
        "goal":{"goal_id":"pilot","kind":"collect","target":"cobblestone","quantity":3},"max_decisions":3600}))
    monkeypatch.setattr(sys,"argv",["mc-diamond","pilot-signal","--config",str(config),"--output",str(tmp_path/"pilot")])
    original_files: dict[Path,bytes]={}
    if reuse_initial:
        assert main()==1
        prior=json.loads(capsys.readouterr().out.splitlines()[-1])["data"]
        assert prior["training"] is None and not prior["signal"]["passed"]
        reference=tmp_path/"pilot/signal"
        original_files={p:p.read_bytes() for p in reference.iterdir() if p.is_file()}
        def no_duplicate_initial(config: Any,path: Path,directory: Path,phase: str,loaded: Any,snapshot: str,**kwargs: Any) -> Any:
            assert phase=="post", "A reference continuation must not rerun initial evaluation"
            return original_evaluate(config,path,directory,phase,loaded,snapshot,**kwargs)
        monkeypatch.setattr(signal_pilot,"evaluate",no_duplicate_initial)
        arguments=["mc-diamond","pilot-signal","--config",str(config),"--output",str(tmp_path/"continuation"),
            "--initial-evaluation-reference",str(reference),"--signal-exception-reason","Explicit test user exception for missing mine_oak_log bad samples"]
        monkeypatch.setattr(sys,"argv",arguments[:-2])
        assert main()==1
        assert "supplied together" in json.loads(capsys.readouterr().out.splitlines()[-1])["data"]["error"]
        expected=json.loads((reference/"manifest.json").read_text())
        from copy import deepcopy
        with pytest.raises(ValueError):
            signal_pilot.initial_reference(reference,{**expected,"moving_threshold":.2},"user exception")
        broken=deepcopy(prior)
        broken["signal"]["by_kind"]["move_oak_log"]["passed"]=False
        (reference/"summary.json").write_text(json.dumps(broken))
        (reference/"signal-check.json").write_text(json.dumps(broken["signal"]))
        with pytest.raises(ValueError,match="other signal checks"):
            signal_pilot.initial_reference(reference,expected,"user exception")
        for name in ("summary.json","signal-check.json"):
            (reference/name).write_bytes(original_files[reference/name])
        from safetensors.torch import load_file,save_file
        from mc_diamond.nanojev import REVISION,WEIGHTS_SHA256
        heads=load_file(str(reference/"initial.safetensors"))
        heads["critics.local.2.bias"]=heads["critics.local.2.bias"]+1.
        save_file(heads,str(reference/"initial.safetensors"),metadata={"revision":REVISION,"initial_weights_sha256":WEIGHTS_SHA256})
        rejected=list(arguments);rejected[5]=str(tmp_path/"mismatched-heads")
        monkeypatch.setattr(sys,"argv",rejected)
        assert main()==1
        rejection=json.loads(capsys.readouterr().out.splitlines()[-1])["data"]
        assert rejection["restored_initial"] and parameter_hash(model)==original
        assert "initial heads differ" in rejection["error"]
        assert rejection["training"] is None and len(rejection["evaluations"])==10
        (reference/"initial.safetensors").write_bytes(original_files[reference/"initial.safetensors"])
        monkeypatch.setattr(sys,"argv",arguments)
    status=main()
    summary=json.loads(capsys.readouterr().out.splitlines()[-1])["data"]
    training=summary["training"]
    assert summary["mock"] and summary["restored_initial"] and parameter_hash(model)==original
    planned=10 if reuse_initial else 20
    if reuse_initial:
        assert not summary["signal"]["passed"] and summary["signal"]["by_kind"]["mine_oak_log"]["bad_n"]==0
        assert summary["user_exception"]["initial_signal_status"]["mine_oak_log"]=="not_assessable_missing_bad_samples"
        assert len(summary["user_exception"]["initial_evaluations"])==10 and summary["planned_slots"]==10
        assert all(p.read_bytes()==contents for p,contents in original_files.items())
    if fail_after_update:
        assert status==1 and len(training["updates"])==1 and training["collected_decisions"]>=128
        assert training["errors"] and not training["usable"]
        assert "Injected failure" in training["episodes"][-1]["error"]["message"]
        assert len(summary["evaluations"])==planned and sum(not r["attempts"] for r in summary["evaluations"])==10
        assert summary["verdict"]=="미판정"
        return
    assert status==0
    assert training["collected_decisions"]==4096 and len(training["updates"])==32
    assert training["unupdated_transitions"]==0 and training["usable"]
    assert summary["halfway"]["decisions"]==2048 and len(training["fixed_reports"])==33
    assert len(summary["evaluations"])==planned and all(r["attempts"] for r in summary["evaluations"])
    assert summary["main_training_decisions"]==0 and summary["planner_calls"]==0
    saved=(tmp_path/"continuation/signal-user-exception") if reuse_initial else (tmp_path/"pilot/signal")
    assert len(list(saved.glob("update-*.safetensors")))==32
    assert len(summary["divergences"])==10
    assert summary["initial_fixed"]["all"]["states"]==(2 if reuse_initial else 1)


def test_first_divergence_reports_policy_drop_and_map_separately(tmp_path: Path) -> None:
    import gzip
    from mc_diamond.signal_diagnostics import divergence
    from copy import deepcopy
    original={"observation":observation().model_dump(),"goal":Goal(goal_id="g",kind="collect",target="oak_log",quantity=3).model_dump(),
        "candidates":{"candidates":[{"candidate_id":f"obs-0:move:{j}","action_kind":"move_observed","params":{},
             "max_ticks":20,"source_obs_id":"obs-0","stop_rule_id":"path","description":desc}
            for j,desc in enumerate(["visible: oak_log 2","visible: stone 1"])],"mask":[True,True],"generated":2},
        "selection":{"candidate_id":"obs-0:move:0"},"step":step(observation()).model_dump(),
        "reward":{"discounted":1.,"discount":.9,"task_terminal":True}}
    before,after=tmp_path/"before.gz",tmp_path/"after.gz"
    def write(path: Path,row: dict[str,Any]) -> None:
        with gzip.open(path,"wt") as handle:
            for kind,data in row.items():
                handle.write(json.dumps({"type":kind,"data":data})+"\n")
    write(before,original)
    write(after,original)
    assert divergence(before,after)["cause"]=="identical"
    row=deepcopy(original); row["selection"]["candidate_id"]="obs-0:move:1"
    write(after,row)
    assert divergence(before,after)["cause"]=="policy"
    row=deepcopy(original); row["observation"]["inventory"]={"oak_log":1}
    write(after,row)
    assert divergence(before,after)["cause"]=="drop_timing"
    row=deepcopy(original); row["observation"]["observed_map"]=[{"block":"dirt","position":[1.,63.,0.]}]
    write(after,row)
    assert divergence(before,after)["cause"]=="map_difference"
