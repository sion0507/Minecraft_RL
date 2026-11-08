import json
import subprocess
import sys
import os
import shutil
import hashlib
from pathlib import Path
from typing import Any

import pytest
import yaml


def run_cli(config: str | Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["mc-diamond", "smoke-episode", "--config", str(config)],
                          text=True, capture_output=True, timeout=15)


def fixture_config(tmp_path: Path, fixture: dict[str, Any]) -> Path:
    fixture_path = tmp_path / "fixture.json"
    fixture_path.write_text(json.dumps(fixture), encoding="utf-8")
    config = yaml.safe_load(Path("configs/pilot.yaml").read_text(encoding="utf-8"))
    config["fixture"] = str(fixture_path)
    config_path = tmp_path / "config.yaml"
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")
    return config_path


def mock_fixture() -> dict[str, Any]:
    result: dict[str, Any] = json.loads(Path("fixtures/mock_episode.json").read_text(encoding="utf-8"))
    return result


def records(result: subprocess.CompletedProcess[str]) -> list[dict[str, Any]]:
    return [json.loads(line) for line in result.stdout.splitlines()]


def test_mock_episode_runs_through_public_cli() -> None:
    result = subprocess.run(
        ["mc-diamond", "smoke-episode", "--config", "configs/pilot.yaml"],
        text=True, capture_output=True, timeout=15,
    )
    assert result.returncode == 0, result.stderr
    records = [json.loads(line) for line in result.stdout.splitlines()]
    assert [record["type"] for record in records] == [
        "reset", "observation", "goal", "candidates", "selection", "step", "reward", "summary"
    ]
    assert records[4]["data"]["candidate_id"] == records[3]["data"]["candidates"][0]["candidate_id"]
    assert records[-1]["data"]["backend"] == "mock"
    assert records[-1]["data"]["goal_completed"] is True
    assert records[-1]["data"]["diamond_success"] is False
    assert records[-1]["data"]["active_ticks"] == 20
    assert records[-1]["data"]["reward_total"] == 1.0
    assert records[-1]["data"]["pause_verified"] is False
    assert records[4]["data"]["probabilities"] is None


def movement_fixture() -> dict[str, Any]:
    fixture = mock_fixture()
    cells = []
    for x in range(3):
        for y, block in [(63, "stone"), (64, "air"), (65, "air")]:
            cells.append({"position": [float(x), float(y), 0.0], "block": block,
                          "passable": block == "air", "support": block == "stone", "hazard": False})
    fixture["initial"].update(position=[0.5, 64.0, 0.5], observed_map=cells, map_version=1)
    fixture["steps"][0]["observation"].update(position=[2.5, 64.0, 0.5], observed_map=cells, map_version=1)
    fixture["steps"][0].update(reason="path_completed", distance_moved=2.0,
                               source_obs_id="obs-0", map_version=1,
                               path=[[1.5, 64.0, 0.5], [2.5, 64.0, 0.5]],
                               stop_evidence=["obs-1", "path_completed"],
                               events=[{"kind": "moved", "source": "mock"}])
    return fixture


def test_movement_death_during_rejected_path_tick_stays_terminal(tmp_path: Path) -> None:
    # The bridge runs one tick for a rejected path; dying then gives invalid=false with path=[].
    fixture = movement_fixture()
    step = fixture["steps"][0]
    step["observation"].update(position=[0.5, 64.0, 0.5], health=0.0, active_ticks=1, remaining_ticks=99)
    step.update(actual_ticks=1, terminated=True, invalid=False, reason="invalid_path", distance_moved=0.0,
                path=[], stop_evidence=["obs-1", "invalid_path"], events=[{"kind": "stopped", "source": "mock"}])
    result = subprocess.run(["mc-diamond", "smoke-movement", "--config", str(fixture_config(tmp_path, fixture))],
                            text=True, capture_output=True, timeout=15)
    summary = records(result)[-1]["data"]
    assert summary["error"] is None, summary["error"]
    assert summary["terminated"] is True
    assert summary["reason"] == "invalid_path"
    assert summary["movement_steps"][0]["path"] == []
    assert summary["movement_completed"] is False


@pytest.mark.parametrize("broken", [None, "source_obs_id", "map_version", "path", "stop_evidence", "events"])
def test_movement_cli_uses_only_observed_clearance_and_support(tmp_path: Path, broken: str | None) -> None:
    fixture = movement_fixture()
    if broken is not None:
        fixture["steps"][0][broken] = {
            "source_obs_id": "stale", "map_version": 99, "path": [],
            "stop_evidence": ["stale", "path_completed"], "events": [],
        }[broken]
    config = fixture_config(tmp_path, fixture)
    result = subprocess.run(["mc-diamond", "smoke-movement", "--config", str(config)],
                            text=True, capture_output=True, timeout=15)
    assert result.returncode == (0 if broken is None else 1), result.stderr
    output = records(result)
    if broken is not None:
        assert output[-1]["data"]["error"]["code"] == "invalid_step"
        assert output[-1]["data"]["movement_completed"] is False
        return
    candidates = next(row["data"] for row in output if row["type"] == "candidates")["candidates"]
    assert len(candidates) == 1
    assert candidates[0]["action_kind"] == "move_observed"
    assert candidates[0]["params"] == {"path": [[1.5, 64.0, 0.5], [2.5, 64.0, 0.5]], "map_version": 1}
    assert candidates[0]["max_ticks"] <= 400
    assert output[-1]["data"]["task"] == "movement_smoke"
    assert output[-1]["data"]["actor_transitions"] == 0
    assert output[-1]["data"]["movement_completed"] is True
    evidence = output[-1]["data"]["movement_steps"][0]
    assert evidence["candidate_id"] == candidates[0]["candidate_id"]
    assert evidence["source_obs_id"] == "obs-0"
    assert evidence["map_version"] == 1
    assert evidence["events"][0]["kind"] == "moved"
    assert evidence["reason"] == "path_completed"
    assert evidence["actual_ticks"] == 20
    assert evidence["wall_seconds"] == 0.0


def test_movement_does_not_route_through_unknown_or_exposed_hazard(tmp_path: Path) -> None:
    fixture = mock_fixture()
    fixture["initial"]["observed_map"] = [
        {"block": "lava", "position": [1.0, 64.0, 0.0], "hazard": True},
        {"block": "stone", "position": [1.0, 63.0, 0.0], "support": True},
    ]
    result = subprocess.run(["mc-diamond", "smoke-movement", "--config", str(fixture_config(tmp_path, fixture))],
                            text=True, capture_output=True, timeout=15)
    assert result.returncode == 1, result.stderr
    output = records(result)
    assert next(row["data"] for row in output if row["type"] == "candidates")["candidates"] == []
    assert next(row["data"] for row in output if row["type"] == "selection")["selector_mode"] == "forced_wait"
    assert output[-1]["data"]["movement_completed"] is False


def step_cells(rise: int, changes: dict[tuple[int, int], dict[str, Any] | None]) -> list[dict[str, Any]]:
    """Start column x=0 on floor y=63; column x=1 has its floor at 63+rise. Air up to y=67; `changes` edit (x, y) cells."""
    def cell(x: int, y: int, block: str) -> dict[str, Any]:
        return {"position": [float(x), float(y), 0.0], "block": block, "passable": block == "air",
                "support": block in {"stone", "slime_block"}, "hazard": False}
    cells = {(x, y): cell(x, y, "stone" if y <= 63 + (rise if x else 0) else "air") for x in range(2) for y in range(60, 68)}
    for point, value in changes.items():
        if value is None:
            del cells[point]
        else:
            cells[point] = {**cells[point], **value}
    return list(cells.values())


STONE = {"block": "stone", "passable": False, "support": True}


@pytest.mark.parametrize("rise, changes, end", [
    (1, {}, [1.5, 65.0, 0.5]),
    (-1, {}, [1.5, 63.0, 0.5]),
    (1, {(0, 67): STONE, (1, 67): STONE}, [1.5, 65.0, 0.5]),  # A 3-high climb: the ceiling is one over the jump's head.
    (2, {}, None), (-2, {}, None),
    (1, {(0, 66): None}, None),  # The jump's head cell over the start column is unobserved ...
    (1, {(0, 66): STONE}, None),  # ... or solid.
    (-1, {(1, 65): STONE}, None),  # The drop's front head cell at the start height.
    (-1, {(1, 62): {"block": "magma_block", "hazard": True}}, None),
    (1, {(0, 63): {"block": "slime_block"}}, None), (-1, {(1, 62): {"block": "slime_block"}}, None),
])
def test_movement_cli_offers_only_observed_one_block_steps(tmp_path: Path, rise: int, changes: dict[tuple[int, int], Any],
                                                           end: list[float] | None) -> None:
    fixture = mock_fixture()
    fixture["initial"].update(position=[0.5, 64.0, 0.5], observed_map=step_cells(rise, changes), map_version=1)
    result = subprocess.run(["mc-diamond", "smoke-movement", "--config", str(fixture_config(tmp_path, fixture))],
                            text=True, capture_output=True, timeout=15)
    candidates = next(row["data"] for row in records(result) if row["type"] == "candidates")["candidates"]
    assert [c["params"]["path"][-1] for c in candidates] == ([end] if end else [])


def test_live_terrain_never_queries_behind_opaque_wall_and_rejects_unknown_route() -> None:
    script = r"""
const assert = require('node:assert/strict')
const {Terrain} = require('./bridge/terrain')
const {Vec3} = require('./bridge/node_modules/vec3')
let hiddenReads = 0
const bot = {entity: {position: new Vec3(0.5, 64, 0.5), eyeHeight: 1.62}, blockAt(p) {
  if (p.x > 2) hiddenReads++
  const name = p.x === 2 || p.y === 63 ? 'stone' : p.x === 0 && p.y === 64 ? 'grass' : 'air'
  return {name, shapes: name === 'stone' ? [[0,0,0,1,1,1]] : []}
}}
const terrain = new Terrain()
terrain.scan(bot)
assert.equal(hiddenReads, 0)
assert(terrain.cells().some(c => c.block === 'stone'))
assert(!terrain.cells().some(c => c.position[0] > 2))
assert.equal(terrain.safe([1.5,64,0.5]), true)
assert.equal(terrain.safe([0.5,64,0.5]), true)
assert.equal(terrain.safe([3.5,64,0.5]), false)
assert.equal(terrain.validPath([0.5,64,0.5], [[1.5,64,0.5]]), true)
assert.equal(terrain.validPath([0.5,64,0.5], [[3.5,64,0.5]]), false)
const resting = {position:[0.5,64,0.5], velocity:[0,-0.0784000015258789,0], on_ground:true, in_liquid:false, on_fire:false}
assert.equal(terrain.stable(resting), true)
assert.equal(terrain.stable({...resting, on_ground:false}), false)
assert.equal(terrain.stable({...resting, velocity:[0.1,-0.0784000015258789,0]}), false)
const before = terrain.version
terrain.scan(bot)
assert.equal(terrain.version, before)
terrain.reset()
assert.deepEqual(terrain.cells(), [])
assert.deepEqual(terrain.visited, [])
let cornerReads = 0
terrain.scan({entity:{position:new Vec3(0.5,62.88,0.5),eyeHeight:1.62}, blockAt(p) {
  if (p.x >= 1 && p.z >= 1) cornerReads++
  const name = p.x === 1 || p.z === 1 ? 'stone' : 'air'
  return {name,shapes:name === 'stone' ? [[0,0,0,1,1,1]] : []}
}})
assert.equal(cornerReads, 0)
"""
    result = subprocess.run(["node", "-e", script], text=True, capture_output=True, timeout=15)
    assert result.returncode == 0, result.stderr


def test_movement_bounds_slippery_surfaces_and_counts_failure_tick_motion() -> None:
    result = subprocess.run(["node", "fixtures/movement_physics.cjs"], text=True, capture_output=True, timeout=15)
    assert result.returncode == 0, result.stderr
    rows = json.loads(result.stdout)
    for row in rows[:-1]:
        assert row["actual_ticks"] <= 400
        assert row["distance_moved"] <= 16, row
        if row["floorName"] in {"ice", "packed_ice", "frosted_ice", "blue_ice"}:
            assert row["reason"] == "invalid_path", row
        else:
            assert row["stable_boundary"] is True, row
            assert row["distance_moved"] > 0, row
    failed = rows[-1]
    assert failed["actual_ticks"] == 1
    assert failed["distance_moved"] == pytest.approx(0.1)
    assert failed["distance_moved"] == pytest.approx(failed["displacement"])
    assert failed["events"][0]["kind"] == "moved"


def test_shipping_movement_climbs_and_drops_one_observed_block_within_the_caps() -> None:
    result = subprocess.run(["node", "fixtures/movement_physics.cjs", "steps"], text=True, capture_output=True, timeout=15)
    assert result.returncode == 0, result.stderr
    rows = {row["floorName"]: row for row in json.loads(result.stdout)}
    for row in rows.values():
        assert 1 <= row["actual_ticks"] <= 400 and row["distance_moved"] <= 16, row
    for name, end in [("step_up", [2, 65, 0]), ("step_down", [2, 63, 0])]:
        assert rows[name]["reason"] == "path_completed" and rows[name]["stable_boundary"], rows[name]
        assert [v // 1 for v in rows[name]["position"]] == end and rows[name]["position"][1] == end[1], rows[name]
    assert rows["step_low"]["reason"] == "path_completed" and rows["step_low"]["position"][1] == 65, rows["step_low"]
    assert rows["step_escape"]["reason"] == "path_completed" and rows["step_escape"]["stable_boundary"], rows["step_escape"]
    for name in ["step_two_up", "step_two_down", "step_unknown", "step_blocked", "step_magma", "step_slime", "step_hazard",
                 "step_closer"]:
        assert rows[name]["reason"] == "invalid_path" and rows[name]["actual_ticks"] == 1, rows[name]
    assert rows["step_pit"]["reason"] == "observed_hazard" and not rows["step_pit"]["stable_boundary"], rows["step_pit"]
    assert rows["step_pit"]["position"][1] > 61, "the fall past the landing stops the walk at once"
    for name in ["step_late_up", "step_late_down"]:  # The step comes after 12 blocks: no new height change near the cap.
        assert rows[name]["reason"] == "distance_limit" and rows[name]["stable_boundary"], rows[name]
        assert rows[name]["position"][1] == 64, rows[name]
    edge = rows["step_edge_down"]  # Already over the edge at 12 blocks: the committed drop lands instead of hanging.
    assert edge["stable_boundary"] and edge["actual_ticks"] < 400 and edge["position"][1] == 63, edge
    sweep = [row for name, row in rows.items() if name.startswith("sweep_")]
    assert len(sweep) == 96 and sum(row["reason"] != "invalid_path" for row in sweep) >= 80
    for row in sweep:  # A late climb or drop settles or completes; it never hangs on an edge until the tick cap.
        assert row["reason"] == "invalid_path" or (row["stable_boundary"] and row["actual_ticks"] < 400), row


@pytest.mark.parametrize("scenario", ["logging", "unchanged", "client", "server", "ticks", "freeze_reply", "mismatch"])
def test_live_bridge_rejects_pause_drift_and_keeps_mineflayer_errors_off_stdout(scenario: str) -> None:
    result = subprocess.run(["node", "fixtures/bridge_contracts.cjs", scenario],
                            text=True, capture_output=True, timeout=10)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == {"passed": True}


def test_information_audit_rejects_mock_as_real_evidence() -> None:
    result = subprocess.run(["mc-diamond", "audit-information", "--config", "configs/pilot.yaml"],
                            text=True, capture_output=True, timeout=10)
    assert result.returncode == 2
    assert records(result)[0]["data"]["code"] == "invalid_config"
    assert records(result)[0]["data"]["message"] == "Actual Minecraft backend required; use configs/minecraft.yaml"


def test_information_audit_fails_when_hidden_variant_changes_policy_input(tmp_path: Path) -> None:
    backend = tmp_path / "information_backend.py"
    backend.write_text(
        "import json,os,sys\n"
        "f=json.load(open('fixtures/mock_episode.json'))\n"
        "fd=int(sys.argv[sys.argv.index('--admin-fd')+1])\n"
        "for line in os.fdopen(fd):\n"
        " r=json.loads(line)\n"
        " variant=r['payload']['variant']\n"
        " print(json.dumps({'request_id':r['request_id'],'result':{'fixture_ready':True}}),flush=True)\n"
        " r=json.loads(sys.stdin.readline())\n"
        " o=f['initial'];o['observed_map']=[];o['health']=20.0 if variant=='ore' else 19.0\n"
        " print(json.dumps({'request_id':r['request_id'],'result':o}),flush=True)\n",
        encoding="utf-8",
    )
    config = yaml.safe_load(Path("configs/minecraft.yaml").read_text())
    config["command"] = [sys.executable, str(backend)]
    config_path = tmp_path / "config.yaml"
    config_path.write_text(yaml.safe_dump(config))
    result = subprocess.run(["mc-diamond", "audit-information", "--config", str(config_path)],
                            text=True, capture_output=True, timeout=10)
    assert result.returncode == 1, result.stderr
    assert records(result)[-1]["type"] == "information_summary"
    assert records(result)[-1]["data"]["information_verified"] is False


@pytest.mark.parametrize(("actual_ticks", "missing_events"), [(20, False), (401, False), (20, True)])
def test_information_audit_checks_complete_evidence_and_tick_bound(tmp_path: Path, actual_ticks: int, missing_events: bool) -> None:
    backend = tmp_path / "audit_backend.py"
    backend.write_text('''import json,os,sys
fd=int(sys.argv[sys.argv.index('--admin-fd')+1])
admin=os.fdopen(fd)
def reply(r,v):
 print(json.dumps({'request_id':r['request_id'],'result':v}),flush=True)
for line in admin:
 r=json.loads(line);p=r['payload'];reply(r,{'fixture_ready':True})
 o=json.load(open('fixtures/mock_episode.json'))['initial']
 o.update(position=[0.5,64.0,0.5],remaining_ticks=1000,map_version=1,observed_map=[])
 for x in range(3):
  for y,block in [(63,'stone'),(64,'air'),(65,'air')]:
   o['observed_map'].append({'block':block,'position':[float(x),float(y),0.0],
      'passable':block=='air','support':block=='stone','hazard':False})
 if p['exposed']:
  o['observed_map'].append({'block':'diamond_ore' if p['variant']=='ore' else 'lava','position':[4.0,64.0,0.0]})
 if p.get('scope') in ['wood','wood_tool']:
  o['observed_map'] += [{'block':'oak_log','position':[1.0,y,0.0],'support':True} for y in [64.0,65.0]]
 if p.get('scope')=='wood_tool':
  o.update(inventory={'wooden_axe':1},tool=None)
 if p.get('scope')=='wood_drop':
  o.update(drops=[{'entity_id':7,'item':'oak_log','quantity':1,'position':o['position']}])
 if p.get('scope')=='empty':
  o['observed_map']=[]
 if p.get('scope') in ['production_craft','production_place','production_furnace','iron','diamond']:
  scope=p['scope']
  o.update(inventory={'iron_ingot':3,'stick':2},observed_map=[])
  if scope=='production_craft': o['observed_map']=[{'block':'crafting_table','position':[1.,64.,0.],'support':True}]
  if scope=='production_place':
   o['inventory']['crafting_table']=1
   o['observed_map']=[{'block':'air','position':[1.,64.,0.],'passable':True},{'block':'stone','position':[1.,63.,0.],'support':True}]
  if scope=='iron':
   o.update(inventory={'stone_pickaxe':1},tool='stone_pickaxe',observed_map=[{'block':'iron_ore','position':[1.,64.,0.],'support':True}])
  if scope=='diamond':
   o.update(inventory={'iron_pickaxe':1},tool='iron_pickaxe',observed_map=[{'block':'diamond_ore','position':[1.,64.,0.],'support':True}])
  if scope=='production_furnace':
   o.update(inventory={'iron_ore':1,'coal':1},observed_map=[{'block':'furnace','position':[1.,64.,0.],'support':True}])
 if str(p.get('scope')).startswith(('stair','tunnel')):
  o.update(inventory={'iron_pickaxe':1},tool='iron_pickaxe',tool_durability=250,on_ground=True)
 if p.get('scope')=='steps':
  o['observed_map']=[{'block':'stone' if y<=63+(x>0) else 'air','position':[float(x),float(y),0.0],'passable':y>63+(x>0),
     'support':y<=63+(x>0),'hazard':False} for x in range(3) for y in range(60,68)]
 r=json.loads(sys.stdin.readline());reply(r,o)
 if not p['exposed']:
  r=json.loads(sys.stdin.readline());c=r['payload']['candidate'];ticks=int(sys.argv[1])
  n={**o,'obs_id':'obs-1','active_ticks':ticks,'remaining_ticks':1000-ticks,'position':[2.5,64.0,0.5]}
  result={'observation':n,'actual_ticks':ticks,'events':[{'kind':'moved','source':'minecraft'}],
    'terminated':False,'truncated':False,'invalid':False,'reason':'path_completed',
    'clock_mode':'paused','pause_verified':True,'stable_boundary':True,'wall_seconds':0.1,
    'source_obs_id':o['obs_id'],'map_version':1,'path':c['params'].get('path',[]),
    'stop_evidence':['obs-1','path_completed'],'distance_moved':2.0}
  if p.get('scope')=='wood':
   n.update(position=o['position'],inventory={'oak_log':2})
   result.update(path=[],reason='cluster_completed',stop_evidence=['obs-1','cluster_completed'],distance_moved=0.0,
      events=[{'kind':'mined','item':'oak_log','quantity':2,'source':'minecraft'},
              {'kind':'acquired','item':'oak_log','quantity':2,'source':'minecraft'}])
  if p.get('scope') in ['wood_tool','wood_drop','empty']:
   ticks=1 if p['scope']=='wood_tool' else c['max_ticks']
   reason='equip_completed' if p['scope']=='wood_tool' else 'wait_completed'
   n.update(position=o['position'],active_ticks=ticks,remaining_ticks=1000-ticks)
   result.update(actual_ticks=ticks,path=[],reason=reason,stop_evidence=['obs-1',reason],distance_moved=0.0,
      events=[{'kind':'equipped' if p['scope']=='wood_tool' else 'wait','source':'minecraft'}])
   if p['scope']=='wood_tool': n.update(tool='wooden_axe')
   if p['scope']=='wood_drop':
    n.update(inventory={'oak_log':1},drops=[])
    result['events'].append({'kind':'acquired','item':'oak_log','quantity':1,'source':'minecraft'})
  if p.get('scope')=='empty' and sys.argv[2]=='1': result['events']=[]
  if str(p.get('scope')).startswith(('stair','tunnel')):
   tunnel=p['scope'].startswith('tunnel')
   for index in range(2 if p['scope'] in ('stair_exposed','stair_iron','tunnel','tunnel_iron') else 1):
    if index:
     r=json.loads(sys.stdin.readline());c=r['payload']['candidate'];o=n
     n={**o,'obs_id':'obs-'+str(index+1)}
    reason=('ore_exposed' if p['variant']=='ore' else 'observed_hazard') if index else 'tunnel_completed' if tunnel else 'stairs_completed'
    n.update(active_ticks=o['active_ticks']+40,remaining_ticks=o['remaining_ticks']-40)
    result.update(observation=n,actual_ticks=40,path=[],reason=reason,source_obs_id=o['obs_id'],stop_evidence=[n['obs_id'],reason],
      distance_moved=0.,events=[{'kind':'tunneled' if tunnel else 'descended','quantity':1,'source':'minecraft'}]*c['params']['cells' if tunnel else 'stairs'])
    if reason=='ore_exposed':
     result['events']=result['events']+[{'kind':'exposed','item':c['params']['stop_blocks'][-1],'position':[4.,99.,0.],'source':'minecraft'}]
    reply(r,result)
   continue
  if p.get('scope')=='steps':
   for index in range(2):
    if index:
     r=json.loads(sys.stdin.readline());c=r['payload']['candidate'];o=n
    n={**o,'obs_id':'obs-'+str(index+1),'active_ticks':o['active_ticks']+ticks,'remaining_ticks':o['remaining_ticks']-ticks,
       'position':c['params']['path'][-1]}
    result.update(observation=n,source_obs_id=o['obs_id'],path=c['params']['path'],stop_evidence=[n['obs_id'],'path_completed'])
    reply(r,result)
   continue
  if p.get('scope') in ['production_craft','production_place','production_furnace','iron','diamond']:
   for index in range(3 if p['scope']=='production_furnace' else 1):
    if index:
     r=json.loads(sys.stdin.readline());c=r['payload']['candidate'];o=n
     n={**o,'obs_id':'obs-'+str(index+1)}
    ticks=200 if c['action_kind']=='wait' else 1
    kind={'craft_batch':'crafted','place_or_equip':'placed','furnace_load':'furnace_loaded','wait':'wait','furnace_collect':'smelted','mine_visible_cluster':'acquired'}[c['action_kind']]
    reason={'crafted':'craft_completed','placed':'place_completed','furnace_loaded':'furnace_loaded','wait':'wait_completed','smelted':'furnace_collected','acquired':'cluster_completed'}[kind]
    item={'crafted':'iron_pickaxe','placed':'crafting_table','furnace_loaded':'iron_ore','wait':None,'smelted':'iron_ingot','acquired':'diamond' if p['scope']=='diamond' else 'iron_ore'}[kind]
    n.update(active_ticks=o['active_ticks']+ticks,remaining_ticks=o['remaining_ticks']-ticks,position=o['position'])
    if kind in ['crafted','smelted','acquired']: n['inventory']={**o['inventory'],item:1}
    if p['scope']=='production_furnace':
     n['furnaces']=[{'position':[1.,64.,0.],'input_item':'iron_ore','input_count':1 if index==0 else 0,'fuel_item':None,'fuel_count':0,'output_item':'iron_ingot' if index==1 else None,'output_count':1 if index==1 else 0,'last_observed_tick':n['active_ticks'] if index!=1 else o['active_ticks']}]
    result.update(observation=n,actual_ticks=ticks,path=[],reason=reason,source_obs_id=o['obs_id'],stop_evidence=[n['obs_id'],reason],distance_moved=0.,events=[{'kind':kind,'item':item,'quantity':1 if item else 0,'source':'minecraft'}])
    reply(r,result)
   continue
  reply(r,result)
''', encoding="utf-8")
    config = yaml.safe_load(Path("configs/minecraft.yaml").read_text())
    config["command"] = [sys.executable, str(backend), str(actual_ticks), "1" if missing_events else "0"]
    config_path = tmp_path / "config.yaml"
    config_path.write_text(yaml.safe_dump(config))
    result = subprocess.run(["mc-diamond", "audit-information", "--config", str(config_path)],
                            text=True, capture_output=True, timeout=10)
    expected = actual_ticks == 20 and not missing_events
    assert result.returncode == (0 if expected else 1), result.stderr
    assert records(result)[-1]["data"]["information_verified"] is expected
    if expected:
        assert {"move_observed_steps", "craft_batch", "facility_place", "furnace_load", "furnace_collect", "iron_mining", "stair_down", "stair_exposure", "stair_iron_exposure",
                "diamond_mining", "tunnel", "tunnel_exposure", "tunnel_iron_exposure"} <= set(
            records(result)[-1]["data"]["scope"])


def test_live_bridge_rejects_policy_administration_before_starting_server() -> None:
    admin_read, admin_write = os.pipe()
    try:
        result = subprocess.run(
            ["node", "bridge/minecraft.js", "--admin-fd", str(admin_read)],
            pass_fds=(admin_read,), text=True, capture_output=True, timeout=10,
            input='{"request_id":"p1","method":"reset","payload":{}}\n'
                  '{"request_id":"p2","method":"clock_trial","payload":{}}\n'
                  '{"request_id":"p3","method":"reset","payload":{},"role":"admin"}\n'
                  '{"request_id":"p4","method":"say","payload":{"command":"secret-marker"}}\n',
        )
    finally:
        os.close(admin_read)
        os.close(admin_write)
    assert result.returncode == 0, result.stderr
    output = records(result)
    assert [r["request_id"] for r in output] == ["p1", "p2", "p3", "p4"]
    assert [r["error"]["code"] for r in output] == [
        "permission_denied", "permission_denied", "invalid_request", "invalid_request",
    ]
    assert "secret-marker" not in result.stdout + result.stderr


def test_information_fixtures_are_forbidden_on_policy_channel() -> None:
    from mc_diamond.rpc import EpisodeError, RpcSession
    with RpcSession(["node", "bridge/minecraft.js"], 5.0) as session:
        with pytest.raises(EpisodeError) as failure:
            session._call("information_fixture", {"variant": "ore", "exposed": False})
        assert failure.value.error.code == "permission_denied"


def test_verify_clock_rejects_mock_as_actual_pause_evidence() -> None:
    result = subprocess.run(["mc-diamond", "verify-clock", "--config", "configs/pilot.yaml"],
                            text=True, capture_output=True, timeout=10)
    assert result.returncode == 2
    assert records(result)[0]["data"]["code"] == "invalid_config"
    assert "Traceback" not in result.stderr


def test_corrupt_snapshot_preserves_current_world_and_hides_admin_state(tmp_path: Path) -> None:
    server = tmp_path / "server"
    (server / "world").mkdir(parents=True)
    original = server / "world" / "player-state"
    original.write_text("preserve-current-world")
    (server / "server.properties").write_text("server-ip=127.0.0.1\nallow-flight=true\n")
    (server / "installation.json").write_text(json.dumps({
        "minecraft": "1.16.5", "eula_accepted_by_user": "2026-11-02", "world_seed": "secret-marker",
    }))
    snapshot = tmp_path / "snapshots" / "C4"
    (snapshot / "world").mkdir(parents=True)
    (snapshot / "world" / "level.dat").write_text("corrupted")
    (snapshot / "snapshot.json").write_text(json.dumps({"task": "C4", "sha256": "0" * 64}))
    config = yaml.safe_load(Path("configs/minecraft.yaml").read_text())
    config["command"] = ["node", "bridge/minecraft.js", "--server-dir", str(server)]
    config_path = tmp_path / "config.yaml"
    config_path.write_text(yaml.safe_dump(config))
    result = run_cli(config_path)
    assert result.returncode == 1
    assert records(result)[-1]["data"]["error"]["code"] == "backend_error"
    assert original.read_text() == "preserve-current-world"
    assert "secret-marker" not in result.stdout + result.stderr


def test_snapshot_root_symlink_cannot_replace_current_world(tmp_path: Path) -> None:
    server = tmp_path / "server"
    (server / "world").mkdir(parents=True)
    original = server / "world" / "player-state"
    original.write_text("preserve-current-world")
    (server / "server.properties").write_text("server-ip=127.0.0.1\nallow-flight=true\n")
    (server / "installation.json").write_text(json.dumps({
        "minecraft": "1.16.5", "eula_accepted_by_user": "2026-11-02",
    }))
    frozen = tmp_path / "frozen"
    frozen.mkdir()
    (frozen / "level.dat").write_bytes(b"valid")
    snapshot = tmp_path / "snapshots" / "C4"
    snapshot.mkdir(parents=True)
    (snapshot / "world").symlink_to(frozen, target_is_directory=True)
    digest = hashlib.sha256(b'["level.dat",5]\nvalid').hexdigest()
    (snapshot / "snapshot.json").write_text(json.dumps({"task": "C4", "sha256": digest}))
    config = yaml.safe_load(Path("configs/minecraft.yaml").read_text())
    config["command"] = ["node", "bridge/minecraft.js", "--server-dir", str(server)]
    config_path = tmp_path / "config.yaml"
    config_path.write_text(yaml.safe_dump(config))
    result = run_cli(config_path)
    assert result.returncode == 1
    assert original.exists() and original.read_text() == "preserve-current-world"
    assert not (server / "world").is_symlink()


def test_rpc_shutdown_waits_for_backend_resource_cleanup(tmp_path: Path) -> None:
    marker = tmp_path / "closed"
    backend = tmp_path / "slow_close.py"
    backend.write_text(
        "import atexit,os,signal,time\nfrom pathlib import Path\n"
        "from mc_diamond.mock_bridge import main\n"
        "def finish(*args):\n"
        " signal.signal(signal.SIGTERM,signal.SIG_IGN)\n"
        " time.sleep(3)\n"
        f" Path({str(marker)!r}).write_text('closed')\n"
        " os._exit(0)\n"
        "signal.signal(signal.SIGTERM,finish);atexit.register(finish)\nmain()\n",
        encoding="utf-8",
    )
    config = yaml.safe_load(Path("configs/pilot.yaml").read_text())
    config.pop("fixture")
    config.update(backend="rpc", command=[sys.executable, str(backend), "--fixture", "fixtures/mock_episode.json"])
    config_path = tmp_path / "config.yaml"
    config_path.write_text(yaml.safe_dump(config))
    result = run_cli(config_path)
    assert result.returncode == 0, result.stderr
    assert marker.exists() and marker.read_text() == "closed"


def test_runtime_hash_tracks_loaded_dependencies_and_added_mods(tmp_path: Path) -> None:
    for name in (".fabric/server/game.jar", "libraries/fabric/loader.jar", "mods/pause.jar",
                 "server.jar", "fabric-server-launch.jar"):
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"original")
    script = (
        "const {Server}=require('./bridge/server');"
        "new Server(process.argv[1]).runtimeHash().then(console.log)"
    )

    def digest() -> str:
        result = subprocess.run(["node", "-e", script, str(tmp_path)],
                                text=True, capture_output=True, check=True, timeout=10)
        return result.stdout.strip()

    original = digest()
    for name in (".fabric/server/game.jar", "libraries/fabric/loader.jar", "mods/pause.jar"):
        target = tmp_path / name
        target.write_bytes(b"modified")
        assert digest() != original
        target.write_bytes(b"original")
        assert digest() == original
    (tmp_path / "mods/extra.jar").write_bytes(b"added")
    assert digest() != original


@pytest.mark.parametrize("changed", ["unchanged", "position", "oxygen", "ticks", "missing_state", "bad_position"])
def test_clock_report_rejects_actual_state_drift(tmp_path: Path, changed: str) -> None:
    # Scripted transport tests the CLI verdict, not Minecraft physics.
    backend = tmp_path / "clock_backend.py"
    backend.write_text(
        "import argparse,json,os,copy\n"
        "p=argparse.ArgumentParser();p.add_argument('--admin-fd',type=int);a=p.parse_args()\n"
        "for line in os.fdopen(a.admin_fd):\n"
        " r=json.loads(line)\n"
        " if r['method']=='certify_clock':\n"
        "  print(json.dumps({'request_id':r['request_id'],'result':{}}),flush=True);continue\n"
        " state={'Motion':'[0.0d,-0.1d,0.0d]','Health':'19.0f','Air':'280s',"
        "'Fire':'20s','Inventory':'[]','FallDistance':'1.0f','HurtTime':'0s'}\n"
        " client={'position':[0.0,64.0,0.0],'velocity':[0.0,-0.1,0.0],'health':19,"
        "'oxygen':280,'on_fire':True,'on_ground':True,'inventory':{},'events':0}\n"
        " before={'client':client,'server':{'position':[0.0,64.0,0.0],'state':state,"
        "'game_ticks':20,'furnace':'CookTime: 5s','drop':'Tags: [mc_clock], Age: 5s'}}\n"
        f" changed={changed!r}\n"
        " if changed=='missing_state':del before['server']['state']['Air']\n"
        " after=copy.deepcopy(before)\n"
        " if changed=='position':after['client']['position'][0]=0.002\n"
        " if changed=='oxygen':after['server']['state']['Air']='279s'\n"
        " if changed=='ticks':after['server']['game_ticks']=21\n"
        " if changed=='bad_position':after['client']['position'][0]=None\n"
        " result={**r['payload'],'before':before,'after':after,'executed_ticks':1,"
        "'wall_seconds':r['payload']['delay_seconds']}\n"
        " print(json.dumps({'request_id':r['request_id'],'result':result}),flush=True)\n",
        encoding="utf-8",
    )
    config = yaml.safe_load(Path("configs/pilot.yaml").read_text(encoding="utf-8"))
    config.pop("fixture")
    config.update(backend="rpc", command=[sys.executable, str(backend)])
    config_path = tmp_path / "config.yaml"
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")
    result = subprocess.run(["mc-diamond", "verify-clock", "--config", str(config_path)],
                            text=True, capture_output=True, timeout=15)
    assert result.returncode == (0 if changed == "unchanged" else 1)
    output = records(result)
    if changed == "bad_position":
        assert output[0]["data"]["code"] == "protocol_error"
        assert output[-1]["type"] == "clock_summary"
        assert output[-1]["data"]["pause_verified"] is False
        assert "Traceback" not in result.stderr
        return
    assert output[-1]["type"] == "clock_summary"
    assert output[-1]["data"]["pause_verified"] is (changed == "unchanged")
    assert output[-1]["data"]["trials"] == 63
    assert all(record["data"]["passed"] is (changed == "unchanged") for record in output[:-1])
    assert all(record["data"]["scene_prepared"] is (changed != "missing_state")
               for record in output[:-1])


@pytest.mark.parametrize("outcome", ["truncated", "invalid"])
def test_episode_outcomes_stay_distinct(tmp_path: Path, outcome: str) -> None:
    fixture = mock_fixture()
    step = fixture["steps"][0]
    step.update(terminated=False, truncated=False, invalid=False, events=[], reason=outcome)
    step[outcome] = True
    result = run_cli(fixture_config(tmp_path, fixture))
    summary = records(result)[-1]["data"]
    assert result.returncode == (1 if outcome == "invalid" else 0)
    assert summary[outcome] is True
    assert summary["terminated"] is False
    assert summary["goal_completed"] is False
    assert summary["active_ticks"] == 20


def test_backend_error_ends_episode_with_summary(tmp_path: Path) -> None:
    fixture = mock_fixture()
    fixture["steps"] = []
    result = run_cli(fixture_config(tmp_path, fixture))
    assert result.returncode == 1
    output = records(result)
    assert [record["type"] for record in output[-2:]] == ["error", "summary"]
    assert output[-1]["data"]["error"]["code"] == "invalid_request"
    assert output[-1]["data"]["goal_completed"] is False
    assert result.stderr


def test_zero_candidates_force_wait_without_actor_experience(tmp_path: Path) -> None:
    fixture = mock_fixture()
    fixture["initial"]["observed_map"] = []
    fixture["steps"][0].update(events=[{"kind": "wait", "quantity": 0, "source": "mock"}],
                                terminated=False, truncated=True, reason="mock_time_limit")
    fixture["steps"][0]["observation"]["inventory"] = {}
    output = records(run_cli(fixture_config(tmp_path, fixture)))
    assert output[3]["data"] == {"candidates": [], "mask": []}
    assert output[4]["data"]["selector_mode"] == "forced_wait"
    assert output[-1]["data"]["actor_transitions"] == 0
    assert output[-1]["data"]["reward_total"] == 0.0


def test_hidden_fixture_fields_are_rejected_without_logging_values(tmp_path: Path) -> None:
    fixture = mock_fixture()
    fixture["initial"]["world_seed"] = "secret-marker"
    result = run_cli(fixture_config(tmp_path, fixture))
    assert result.returncode == 1
    assert records(result)[-1]["data"]["error"] is not None
    assert "secret-marker" not in result.stdout + result.stderr


@pytest.mark.parametrize("reply, expected", [
    ('print(\'{"request_id":"wrong","result":{}}\', flush=True)', "protocol_error"),
    ('print("not json", flush=True)', "protocol_error"),
    ('import time; time.sleep(5)', "timeout"),
])
def test_rpc_failure_is_bounded_and_reported(tmp_path: Path, reply: str, expected: str) -> None:
    backend = tmp_path / "backend.py"
    backend.write_text(reply, encoding="utf-8")
    config = yaml.safe_load(Path("configs/pilot.yaml").read_text(encoding="utf-8"))
    config.pop("fixture")
    config.update(backend="rpc", command=[sys.executable, str(backend)], rpc_timeout_seconds=0.2)
    config_path = tmp_path / "config.yaml"
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")
    result = run_cli(config_path)
    assert result.returncode == 1
    assert records(result)[-1]["data"]["error"]["code"] == expected


def test_alternate_rpc_backend_uses_the_same_public_flow(tmp_path: Path) -> None:
    # Alternate RPC entry point: only transport configuration changes, not episode execution.
    config = yaml.safe_load(Path("configs/pilot.yaml").read_text(encoding="utf-8"))
    config.pop("fixture")
    config.update(backend="rpc", command=[sys.executable, "-m", "mc_diamond.mock_bridge",
                  "--fixture", str(Path("fixtures/mock_episode.json").resolve())])
    config_path = tmp_path / "config.yaml"
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")
    result = run_cli(config_path)
    assert result.returncode == 0
    assert records(result)[-1]["data"]["clock_mode"] == "mock"


def test_tick_mismatch_cannot_report_completed_goal(tmp_path: Path) -> None:
    fixture = mock_fixture()
    fixture["steps"][0]["observation"]["active_ticks"] = 99
    result = run_cli(fixture_config(tmp_path, fixture))
    summary = records(result)[-1]["data"]
    assert result.returncode == 1
    assert summary["error"]["code"] == "invalid_step"
    assert summary["goal_completed"] is False


def test_doctor_reports_actual_cpu_computation() -> None:
    result = subprocess.run(["mc-diamond", "doctor", "--config", "configs/pilot.yaml"],
                            text=True, capture_output=True, timeout=60)
    output = records(result)
    assert len(output) == 1
    report = output[0]["data"]
    assert output[0]["type"] == "doctor"
    assert report["probes"]["python"]["status"] == "available"
    assert report["probes"]["python"]["computation"] == {"expected": 10, "actual": 10}
    assert report["minecraft_verified"] is False
    assert report["probes"]["gpu"]["status"] in {"available", "missing", "error"}
    assert result.returncode == (0 if report["ready"] else 1)


def test_doctor_distinguishes_missing_tools_and_execution_errors(tmp_path: Path) -> None:
    # A controlled external tool failure, through the same CLI as real hardware probes.
    node = tmp_path / "node"
    node.write_text("#!/bin/sh\nexit 7\n", encoding="utf-8")
    node.chmod(0o755)
    executable = shutil.which("mc-diamond")
    assert executable is not None
    result = subprocess.run([executable, "doctor", "--config", "configs/pilot.yaml"],
                            env={**os.environ, "PATH": str(tmp_path)},
                            text=True, capture_output=True, timeout=60)
    probes = records(result)[0]["data"]["probes"]
    assert result.returncode == 1
    assert probes["node"]["status"] == "error"
    assert probes["java"]["status"] == "missing"
    assert probes["gpu"]["status"] == "missing"


def test_backend_launch_failure_still_has_episode_summary(tmp_path: Path) -> None:
    config = yaml.safe_load(Path("configs/pilot.yaml").read_text(encoding="utf-8"))
    config.pop("fixture")
    config.update(backend="rpc", command=[str(tmp_path / "missing-backend")])
    config_path = tmp_path / "config.yaml"
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")
    result = run_cli(config_path)
    assert result.returncode == 1
    output = records(result)
    assert [record["type"] for record in output] == ["error", "summary"]
    assert output[-1]["data"]["error"]["code"] == "backend_error"
    assert output[-1]["data"]["episode_id"]
    assert output[-1]["data"]["attempt_id"]


def test_policy_rpc_cannot_reset_or_spoof_administrator() -> None:
    admin_read, admin_write = os.pipe()
    try:
        result = subprocess.run(
            [sys.executable, "-m", "mc_diamond.mock_bridge", "--fixture", "fixtures/mock_episode.json",
             "--admin-fd", str(admin_read)], pass_fds=(admin_read,), text=True, capture_output=True,
            input='{"request_id":"p1","method":"reset","payload":{}}\n'
                  '{"request_id":"p2","method":"reset","payload":{},"role":"admin"}\n', timeout=5,
        )
    finally:
        os.close(admin_read)
        os.close(admin_write)
    output = [json.loads(line) for line in result.stdout.splitlines()]
    assert output[0]["error"]["code"] == "permission_denied"
    assert output[1]["error"]["code"] == "invalid_request"
    assert output[1]["request_id"] == "p2"


def test_goal_completion_preserves_acquisitions_across_decisions(tmp_path: Path) -> None:
    fixture = mock_fixture()
    first = fixture["steps"][0]
    first.update(terminated=False, reason="mock_acquisition")
    first["observation"]["inventory"] = {"oak_log": 1}
    last = json.loads(json.dumps(first))
    last.update(terminated=True, reason="mock_goal_completed", events=[{"kind": "wait", "source": "mock"}])
    last["observation"].update(obs_id="obs-2", active_ticks=40, remaining_ticks=60)
    fixture["steps"].append(last)
    result = run_cli(fixture_config(tmp_path, fixture))
    assert result.returncode == 0
    assert records(result)[-1]["data"]["goal_completed"] is True


@pytest.mark.parametrize("mode, verified, expected", [
    ("realtime", False, 0), ("paused", True, 0), ("paused", False, 1), ("unverified", False, 1),
    ("recertified", True, 1), ("revoked", False, 1),
])
def test_rpc_wire_can_carry_actual_backend_provenance(tmp_path: Path, mode: str, verified: bool, expected: int) -> None:
    # Scripted external RPC replies test compatibility; this is not Minecraft verification.
    fixture = mock_fixture()
    fixture["steps"][0]["events"][0]["source"] = "minecraft"
    fixture["steps"][0].update(clock_mode=mode, pause_verified=verified)
    if mode in {"recertified", "revoked"}:
        first = fixture["steps"][0]
        first.update(terminated=False, clock_mode="unverified" if verified else "paused", pause_verified=not verified)
        last = json.loads(json.dumps(first))
        last.update(terminated=True, clock_mode="paused" if verified else "unverified", pause_verified=verified)
        last["observation"].update(obs_id="obs-2", active_ticks=40, remaining_ticks=60)
        fixture["steps"].append(last)
    fixture_path = tmp_path / "wire.json"
    fixture_path.write_text(json.dumps(fixture), encoding="utf-8")
    backend = tmp_path / "backend.py"
    backend.write_text(
        "import argparse,json,os,sys\n"
        "parser=argparse.ArgumentParser();parser.add_argument('--admin-fd',type=int);args=parser.parse_args()\n"
        f"fixture=json.load(open({str(fixture_path)!r}))\n"
        "request=json.loads(os.fdopen(args.admin_fd).readline())\n"
        "ids=request['payload'];observation=fixture['initial'];observation.update(ids)\n"
        "print(json.dumps({'request_id':request['request_id'],'result':observation}),flush=True)\n"
        "index=0\n"
        "for line in sys.stdin:\n"
        " request=json.loads(line)\n"
        " if request['method']=='observe': result=observation\n"
        " else:\n"
        "  result=fixture['steps'][index];result['observation'].update(ids);index+=1\n"
        " print(json.dumps({'request_id':request['request_id'],'result':result}),flush=True)\n",
        encoding="utf-8",
    )
    config = yaml.safe_load(Path("configs/pilot.yaml").read_text(encoding="utf-8"))
    config.pop("fixture")
    config.update(backend="rpc", command=[sys.executable, str(backend)])
    config_path = tmp_path / "config.yaml"
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")
    result = run_cli(config_path)
    assert result.returncode == expected, result.stderr
    output = records(result)
    summary = output[-1]["data"]
    assert summary["pause_verified"] is (mode == "paused" and verified)
    if expected:
        assert summary["clock_mode"] == "unverified"
        return
    assert output[5]["data"]["events"][0]["source"] == "minecraft"
    assert summary["clock_mode"] == mode
    assert output[-1]["data"]["diamond_success"] is False
