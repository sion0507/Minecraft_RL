// Shipping policy dispatch with scripted transport; not actual game certification.
const assert = require('node:assert/strict')
const vm = require('node:vm')
const { EventEmitter } = require('node:events')
const loadBridge = require('./bridge_harness.cjs')
const { Server } = require('../bridge/server')

async function transport (scenario) {
  const server = new Server('/unused')
  const client = new EventEmitter()
  const child = new EventEmitter()
  child.exitCode = null
  let writes = 0
  child.stdin = { write (line) {
    writes++
    const match = line.match(/^mcdiamond_step 1 ([0-9a-f-]{36})\n$/)
    assert.ok(match, 'one administrator command without a say marker')
    queueMicrotask(() => {
      client.emit('custom_payload', { channel: 'other:channel', data: Buffer.from('ignored') })
      client.emit('custom_payload', { channel: 'mcdiamond:tick', data: Buffer.from('old-nonce 0 1') })
      if (scenario === 'disconnect') return client.emit('end')
      if (scenario === 'exit') return child.emit('exit')
      client.emit('custom_payload', { channel: 'mcdiamond:tick',
        data: Buffer.from(match[1] + (scenario === 'malformed' ? ' NaN 1' : ' 123 124')) })
    })
  } }
  server.process = child
  if (scenario === 'normal') assert.deepEqual(await server.step(client, 1), { before: 123, after: 124 })
  else await assert.rejects(server.step(client, 1), scenario === 'malformed' ? /Invalid server tick receipt/ : /exited during tick/)
  assert.equal(writes, 1)
  assert.equal(client.listenerCount('custom_payload'), 0)
  assert.equal(client.listenerCount('end'), 0)
  assert.equal(child.listenerCount('exit'), 0)
}

async function check (scenario) {
  const c = loadBridge({ scenario, EventEmitter })
  vm.runInContext(`
    episode={episode_id:'ticks',attempt_id:'fixture'}; frozen=connected=pauseVerified=true
    bot=new EventEmitter(); bot.physicsEnabled=false;bot.health=20
    bot.inventory={items:()=>[]}
    bot.clearControlStates=()=>{bot.cleared=true}
    var progressed=0; var calls=0; var physical=0; var received=false
    bot.on('physicsTick',()=>physical++)
    const state={position:[0,64,0],velocity:[0,0,0],health:20,oxygen:300,on_fire:false,
      on_ground:true,in_liquid:false,inventory:{},tool:null,tool_durability:null,map_version:1}
    terrain.danger=()=>false;terrain.stable=()=>true
    observation=async()=>{
      assertReceived()
      return {...episode,...state,obs_id:observationId(),active_ticks:activeTicks,
        remaining_ticks:budget-activeTicks,observed_map:[],drops:[],furnaces:[]}
    }
    function assertReceived(){if(calls&&!received)throw Error('observed before tick packets')}
    server.gameTime=async()=>{throw Error('per-tick console polling')}
    server.step=async(client,n)=>{
      calls++;received=false
      assertOne(n)
      const before=progressed;progressed+=scenario==='extra_tick'?2:1
      const physics=()=>{for(let i=0;i<4;i++)if(bot.physicsEnabled)bot.emit('physicsTick')}
      if(scenario==='late_physics')setTimeout(physics,8);else physics()
      await new Promise(resolve=>setTimeout(resolve,2))
      if(scenario==='damage')state.health=19
      received=true
      return {before,after:progressed}
    }
    function assertOne(n){if(n!==1)throw Error('batched macro tick')}
    bot._client=new EventEmitter()
    pause=async()=>{}
  `, c)
  const initial = await c.observation()
  const candidate = { candidate_id: 'wait', action_kind: 'wait', params: {}, max_ticks: 20,
    stop_rule_id: 'wait_or_hazard', source_obs_id: initial.obs_id, description: 'wait' }
  const request = { request_id: 'tick-contract', method: 'step', payload: { candidate } }
  if (scenario === 'extra_tick') {
    await assert.rejects(c.dispatch(request, false), /Unexpected server tick duration/)
    assert.equal(vm.runInContext('activeTicks', c), 2, 'preserve unexpected elapsed ticks')
  } else {
    const step = await c.dispatch(request, false)
    assert.equal(step.actual_ticks, scenario === 'damage' ? 1 : 20)
    assert.equal(step.observation.health, scenario === 'damage' ? 19 : 20)
    assert.equal(vm.runInContext('calls', c), step.actual_ticks)
    assert.equal(vm.runInContext('physical', c), step.actual_ticks, 'one client physics tick per server tick')
  }
  assert.equal(vm.runInContext('bot.physicsEnabled', c), false)
  assert.equal(vm.runInContext('bot.cleared', c), true)
}

async function main () {
  for (const scenario of ['normal', 'malformed', 'disconnect', 'exit']) await transport(scenario)
  for (const scenario of ['normal', 'late_physics', 'damage', 'extra_tick']) await check(scenario)
  process.stdout.write(JSON.stringify({ passed: true }) + '\n')
}
main().catch(error => { console.error(error); process.exitCode = 1 })
