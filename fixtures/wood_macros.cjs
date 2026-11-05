// Scripted transport/physics checks against the shipping bridge; not actual game evidence.
const assert = require('node:assert/strict')
const vm = require('node:vm')
const loadBridge = require('./bridge_harness.cjs')
const { EventEmitter } = require('node:events')

async function completedBreakInterruptions () {
  for (const stop of ['hazard', 'tool_broken', 'death']) {
    const c = loadBridge({ stop })
    vm.runInContext(`
      episode={episode_id:'completion',attempt_id:'test'}; frozen=connected=pauseVerified=true
      const state={position:[0.5,64,0.5],velocity:[0,0,0],health:20,oxygen:300,on_fire:false,
        on_ground:true,in_liquid:false,tool:stop==='tool_broken'?'wooden_axe':null,tool_durability:1,
        inventory:{},map_version:1}
      const cell={block:'oak_log',position:[1,64,0],support:true,passable:false,hazard:false}
      terrain.memory.set('1,64,0',cell); terrain.visible=new Set(['1,64,0'])
      terrain.danger=s=>s.on_fire; terrain.stable=s=>!s.on_fire && s.health>0; terrain.safe=()=>false
      let finishing=false
      bot={entity:{position:new Vec3(0.5,64,0.5),eyeHeight:1.62},inventory:{items:()=>[]},heldItem:null,
        clearControlStates(){},lookAt:async()=>{},swingArm(){},digTime:()=>50,
        blockAt:p=>({position:p,name:cell.block}),_client:{write(name,packet){if(packet.status===2)finishing=true}}}
      observation=async()=>({...episode,...state,obs_id:observationId(),active_ticks:activeTicks,
        remaining_ticks:budget-activeTicks,observed_map:[cell]})
      advance=async n=>{activeTicks+=n;if(finishing){cell.block='air';
        if(stop==='hazard')state.on_fire=true
        if(stop==='tool_broken')state.tool=null
        if(stop==='death')state.health=0
      }return n}
      pause=async()=>{}
      var candidate={candidate_id:'completion-log',action_kind:'mine_visible_cluster',
        params:{block:'oak_log',blocks:[[1,64,0]],map_version:1},max_ticks:400,
        stop_rule_id:'wood_or_hazard',source_obs_id:observationId(),description:'one visible log'}
    `, c)
    const result = await c.dispatch({ request_id: stop, method: 'step', payload: { candidate: c.candidate } }, false)
    assert.equal(result.actual_ticks, 2)
    assert.equal(result.reason, stop === 'hazard' ? 'observed_hazard' : stop)
    assert.equal(result.events.filter(e => e.kind === 'mined').length, 1)
    assert.equal(vm.runInContext('minedTargets[0].confirmed', c), true)
    vm.runInContext(`
      inventory=()=>({oak_log:1}); acquisitionBaseline={}
      drops.set(70,{target:minedTargets[0],collected:true,item:'oak_log',quantity:1,
        entity_id:70,position:[1.5,64,0.5]})
    `, c)
    assert.equal(c.drainEvents().filter(e => e.kind === 'acquired').length, 1)
    assert.equal(c.drainEvents().length, 0)
  }
}

async function dropProvenance () {
  const c = loadBridge({ EventEmitter })
  const mineflayer = require('../bridge/node_modules/mineflayer')
  const original = mineflayer.createBot
  vm.runInContext(`
    mineflayer.createBot = () => {
      const b = new EventEmitter()
      b.entity = {id: 1}
      b.inventory = {items: () => [{name:'oak_log', count:1}]}
      setTimeout(() => b.emit('spawn'), 0)
      return b
    }
  `, c)
  try {
    await c.connect()
    for (const scenario of ['expired', 'failed', 'confirmed']) {
      c.scenario = scenario
      vm.runInContext(`
        activeTicks = 100; acquisitionBaseline = {}; drops.clear(); pendingEvents = []
        minedTargets = [{block:'oak_log', position:[1,64,0], tick:scenario === 'expired' ? 0 : 100,
          confirmed:scenario !== 'failed'}]
        var supplied = {id:70, position:new Vec3(1.5,64.5,0.5),
          getDroppedItem:() => ({name:'oak_log', count:1})}
        bot.emit('itemDrop', supplied)
        bot.emit('playerCollect', bot.entity, supplied)
      `, c)
      const events = c.drainEvents()
      assert.equal(events.length, scenario === 'confirmed' ? 1 : 0)
      if (events.length) assert.equal(events[0].entity_id, 70)
    }
  } finally { mineflayer.createBot = original }
}

async function main () {
  const context = loadBridge()
  vm.runInContext(`
    episode = {episode_id: 'test', attempt_id: 'test'}
    frozen = connected = pauseVerified = true
    previousPhysics = true
    const state = {position: [0.5, 64, 0.5], velocity: [0, 0, 0], health: 20,
      on_ground: true, in_liquid: false, on_fire: false, tool: null, inventory: {}, map_version: 1}
    const cell = {block: 'oak_log', position: [1, 64, 0], support: true, passable: false, hazard: false}
    terrain.memory.set('1,64,0', cell)
    terrain.visible = new Set(['1,64,0'])
    terrain.danger = () => false
    terrain.stable = () => true
    terrain.safe = () => false
    bot = {entity: {position: new Vec3(0.5, 64, 0.5), eyeHeight: 1.62},
      inventory: {items: () => []}, clearControlStates () {}, lookAt: async () => {}, swingArm () {},
      digTime: () => 3000, heldItem: null,
      blockAt (p) { if (p.toString() !== '(1, 64, 0)') throw Error('hidden query'); return {position:p, name:'oak_log'} },
      _client: {write (name, packet) { if (packet.status === 2) cell.block = 'air' }}}
    observation = async () => ({...episode, ...state, obs_id: observationId(),
      active_ticks: activeTicks, remaining_ticks: budget - activeTicks, observed_map: [cell]})
    advance = async ticks => {activeTicks += ticks; return ticks}
    pause = async () => {}
    candidateFor = () => ({candidate_id:'wood', action_kind:'mine_visible_cluster',
      params:{block:'oak_log',blocks:[[1,64,0]],map_version:1}, max_ticks:400,
      stop_rule_id:'wood_or_hazard', source_obs_id:observationId(), description:'one log'})
  `, context)
  const mined = await context.dispatch({ request_id: '1', method: 'step', payload: { candidate: context.candidateFor() } }, false)
  assert.equal(mined.invalid, false)
  assert.equal(mined.events.filter(e => e.kind === 'mined').length, 1)
  assert.equal(mined.events.some(e => e.kind === 'acquired'), false)
  assert.ok(mined.actual_ticks >= 60 && mined.actual_ticks <= 400)
  for (const ticks of [20, 100, 200]) {
    const c = context.candidateFor()
    c.action_kind = 'wait'; c.params = {}; c.max_ticks = ticks
    const result = await context.dispatch({ request_id: 'wait', method: 'step', payload: { candidate: c } }, false)
    assert.equal(result.actual_ticks, ticks)
    assert.equal(result.events[0].kind, 'wait')
  }
  vm.runInContext("state.on_fire = true; terrain.danger = () => true", context)
  const hazard = await context.dispatch({ request_id: 'hazard', method: 'step', payload: { candidate: context.candidateFor() } }, false)
  assert.equal(hazard.actual_ticks, 1)
  assert.equal(hazard.reason, 'observed_hazard')
  assert.equal(hazard.events.some(e => e.kind === 'mined'), false)
  vm.runInContext(`
    state.on_fire = false
    terrain.danger = () => false
    cell.block = 'oak_log'
    state.tool = 'wooden_axe'; state.tool_durability = 1
    advance = async ticks => { activeTicks += ticks; state.tool_durability = 0; return ticks }
  `, context)
  const broken = await context.dispatch({ request_id: 'broken', method: 'step', payload: { candidate: context.candidateFor() } }, false)
  assert.equal(broken.reason, 'tool_broken')
  assert.equal(broken.actual_ticks, 1)
  assert.equal(broken.events.some(e => e.kind === 'mined'), false)
  vm.runInContext("state.tool = null; advance = async ticks => {activeTicks += ticks; return ticks}", context)
  const old = context.candidateFor()
  const short = context.candidateFor(); short.max_ticks = 5
  const bounded = await context.dispatch({ request_id: 'short', method: 'step', payload: { candidate: short } }, false)
  assert.equal(bounded.actual_ticks, 5)
  assert.equal(bounded.reason, 'macro_tick_limit')
  assert.equal(bounded.events.some(e => e.kind === 'mined'), false)
  old.max_ticks = 5
  const cancelled = await context.dispatch({ request_id: 'stale', method: 'step', payload: { candidate: old } }, false)
  assert.equal(cancelled.cancelled, true)
  assert.equal(cancelled.reason, 'candidate_invalidated')
  assert.equal(cancelled.events[0].kind, 'wait')
  assert.equal(cancelled.actual_ticks, 5)
  assert.equal(cancelled.invalid, false)
  for (const label of ['time_or_hazard', 'cancelled_selection']) {
    const forged = context.candidateFor()
    Object.assign(forged, { action_kind: 'wait', params: {}, max_ticks: 7, stop_rule_id: label })
    const rejected = await context.dispatch({ request_id: label, method: 'step', payload: { candidate: forged } }, false)
    assert.equal(rejected.invalid, true)
    assert.equal(rejected.reason, 'invalid_wait')
  }
  const noCandidates = context.candidateFor()
  Object.assign(noCandidates, { action_kind: 'wait', params: {}, max_ticks: 20, stop_rule_id: 'no_candidates' })
  const plainWait = await context.dispatch({ request_id: 'forged-failure', method: 'step', payload: { candidate: noCandidates } }, false)
  assert.equal(plainWait.events.some(e => e.kind === 'failed'), false)
  vm.runInContext('activeTicks = budget - 350', context)
  const tooLong = context.candidateFor()
  Object.assign(tooLong, { action_kind: 'wait', params: {}, max_ticks: 350 })
  const rejected = await context.dispatch({ request_id: 'remaining-budget', method: 'step', payload: { candidate: tooLong } }, false)
  assert.equal(rejected.invalid, true)
  assert.equal(rejected.actual_ticks, 1)
  vm.runInContext('activeTicks = budget - 7', context)
  const clipped = context.candidateFor()
  Object.assign(clipped, { action_kind: 'wait', params: {}, max_ticks: 7 })
  const last = await context.dispatch({ request_id: 'clipped', method: 'step', payload: { candidate: clipped } }, false)
  assert.equal(last.invalid, false)
  assert.equal(last.actual_ticks, 7)
  assert.equal(last.truncated, true)
  await dropProvenance()
  await completedBreakInterruptions()
  process.stdout.write(JSON.stringify({ passed: true }) + '\n')
}
main().catch(error => { console.error(error); process.exitCode = 1 })
