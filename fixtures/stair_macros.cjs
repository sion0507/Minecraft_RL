// Shipping stair macro over installed physics and a scripted server; never Minecraft evidence.
const assert = require('node:assert/strict')
const vm = require('node:vm')
const loadBridge = require('./bridge_harness.cjs')
const { Physics, PlayerState } = require('../bridge/node_modules/prismarine-physics')
const { Vec3 } = require('../bridge/node_modules/vec3')
const data = require('../bridge/node_modules/minecraft-data')('1.16.5')
const Block = require('../bridge/node_modules/prismarine-block')('1.16.5')

const plain = value => JSON.parse(JSON.stringify(value))

// Standing on y=64 at (0,65,0); everything east of x=1 is rock up to y=70.
function scene ({ blocks = {}, tool = 'iron_pickaxe', durability = 250, digTicks = 3, position = [0.5, 65, 0.5],
  onGround = true, onDig = null } = {}) {
  const changed = new Map(Object.entries(blocks))
  const name = ({ x, y, z }) => changed.get([x, y, z].join(',')) ?? (y < 65 || (x >= 1 && y <= 70) ? 'stone' : 'air')
  const world = { getBlock (point) {
    const cell = point.floored()
    const block = new Block(data.blocksByName[name(cell)].id, 0, 0)
    block.position = cell
    return block
  } }
  const reads = new Set()
  const control = { forward: false, back: false, left: false, right: false, jump: false, sprint: false, sneak: false }
  const dug = []
  const bot = {
    entity: { position: new Vec3(...position), velocity: new Vec3(0, -0.0784, 0), onGround, yaw: -Math.PI / 2, pitch: 0,
      effects: {}, eyeHeight: 1.62, metadata: { 0: 0, 1: 300 } },
    jumpTicks: 0, jumpQueued: false, fireworkRocketDuration: 0, version: '1.16.5', health: 20, entities: {}, physicsEnabled: false,
    heldItem: tool ? { name: tool, maxDurability: 250, durabilityUsed: 250 - durability } : null,
    inventory: { slots: [], items: () => bot.heldItem ? [{ name: bot.heldItem.name, count: 1 }] : [] },
    blockAt (point) { reads.add(point.toArray().join(',')); return world.getBlock(point) },
    digTime: () => digTicks * 50, swingArm () {},
    setControlState (key, value) { control[key] = value },
    clearControlStates () { for (const key of Object.keys(control)) control[key] = false },
    async lookAt (point) { const delta = point.minus(this.entity.position); this.entity.yaw = Math.atan2(-delta.x, -delta.z) },
    _client: { write (packet, { status, location }) {
      if (status !== 2) return
      changed.set(location.toArray().join(','), 'air')
      dug.push(location.toArray())
      if (onDig) onDig(location.toArray(), changed)
      if (bot.heldItem && ++bot.heldItem.durabilityUsed >= 250) bot.heldItem = null
    } }
  }
  const physics = Physics(data, world)
  const c = loadBridge({ fixtureBot: bot })
  vm.runInContext(`bot = fixtureBot; episode = { episode_id: 'stair', attempt_id: 'fixture' }
    frozen = connected = pauseVerified = true; pause = async () => {}`, c)
  c.advance = async () => {
    if (bot.health > 0) physics.simulatePlayer(new PlayerState(bot, control), world).apply(bot)
    bot.clearControlStates()
    vm.runInContext('activeTicks++', c)
    if (c.afterTick) c.afterTick(bot)
    return 1
  }
  const observe = async () => plain(await c.dispatch({ request_id: 'observe', method: 'observe', payload: {} }, false))
  const stair = async (params = {}, maxTicks = 400) => {
    const state = await observe()
    const candidate = { candidate_id: 'stair', action_kind: 'stair_down', max_ticks: maxTicks, stop_rule_id: 'stair',
      source_obs_id: state.obs_id, description: 'stair',
      params: { direction: [1, 0], stairs: 1, stop_blocks: ['diamond_ore'], map_version: state.map_version, ...params } }
    return plain(await c.dispatch({ request_id: 'step', method: 'step', payload: { candidate } }, false))
  }
  const wait = async () => {
    const state = await observe()
    return plain(await c.dispatch({ request_id: 'wait', method: 'step', payload: { candidate: { candidate_id: 'hold',
      action_kind: 'wait', params: {}, max_ticks: 20, stop_rule_id: 'hold', source_obs_id: state.obs_id, description: 'hold' } } }, false))
  }
  return { c, bot, dug, reads, changed, observe, stair, wait }
}

const kinds = (step, kind) => step.events.filter(event => event.kind === kind)

async function main () {
  {
    const s = scene()
    const step = await s.stair({ stairs: 4 })
    assert.equal(step.reason, 'stairs_completed')
    assert.equal(step.invalid, false)
    assert.equal(step.stable_boundary, true)
    assert.ok(step.actual_ticks >= 1 && step.actual_ticks <= 400, 'tick accounting')
    assert.deepEqual(step.observation.position.map(Math.floor).slice(0, 2), [4, 61], 'four stairs east and down')
    assert.equal(step.observation.position[1], 61, 'stands on an observed floor')
    assert.equal(kinds(step, 'descended').length, 4)
    assert.equal(kinds(step, 'mined').length, 12)
    assert.deepEqual(s.dug.slice(0, 6), [[1, 66, 0], [1, 65, 0], [1, 64, 0], [2, 65, 0], [2, 64, 0], [2, 63, 0]], 'top-down so each cut exposes the next cell')
    assert.deepEqual(step.path, [[1.5, 64, 0.5], [2.5, 63, 0.5], [3.5, 62, 0.5], [4.5, 61, 0.5]])
    assert.ok(step.distance_moved > 4)
    assert.equal(step.observation.health, 20)
    assert.equal(step.observation.hidden_hazard_peek, false)
  }
  {
    const baseline = await scene().stair({ stairs: 2 })
    for (const hidden of ['diamond_ore', 'lava', 'water']) {
      const s = scene({ blocks: { '4,64,3': hidden } })
      const step = await s.stair({ stairs: 2 })
      assert.equal(step.reason, 'stairs_completed', hidden)
      assert.equal(step.actual_ticks, baseline.actual_ticks, hidden)
      assert.deepEqual(step.observation.position, baseline.observation.position, hidden)
      assert.equal(s.reads.has('4,64,3'), false, 'hidden cell never read')
    }
  }
  {
    const s = scene({ blocks: { '3,63,0': 'diamond_ore' } })
    const step = await s.stair({ stairs: 4 })
    assert.equal(step.reason, 'ore_exposed')
    assert.equal(kinds(step, 'exposed')[0].item, 'diamond_ore')
    assert.deepEqual(kinds(step, 'exposed')[0].position, [3, 63, 0])
    assert.equal(step.stable_boundary, true)
    assert.equal(step.stop_evidence[1], 'ore_exposed')
    const next = await s.stair({ stairs: 1 })
    assert.equal(next.reason, 'stairs_completed', 'the same exposure must not stop again')
    assert.equal(kinds(next, 'exposed').length, 0)
    const blocked = await s.stair({ stairs: 1 })
    assert.equal(blocked.reason, 'ore_in_path', 'a stop ore is never cut by the descent')
    assert.equal(s.dug.some(point => point.join(',') === '3,63,0'), false)
  }
  {
    const s = scene({ blocks: { '3,63,0': 'coal_ore' } })
    const step = await s.stair({ stairs: 2 })
    assert.equal(step.reason, 'stairs_completed', 'other ore stays on the map only')
    assert.ok(step.observation.observed_map.some(cell => cell.block === 'coal_ore'))
    assert.equal(kinds(step, 'exposed').length, 0)
  }
  {
    const s = scene({ blocks: { '3,63,0': 'iron_ore' } })
    const step = await s.stair({ stairs: 2, stop_blocks: ['diamond_ore', 'iron_ore'] })
    assert.equal(step.reason, 'ore_exposed', 'goal ore stops')
    assert.equal(kinds(step, 'exposed')[0].item, 'iron_ore')
  }
  {
    const s = scene({ blocks: { '1,63,0': 'lava' } })
    const step = await s.stair({ stairs: 1 })
    assert.equal(step.reason, 'observed_hazard')
    assert.equal(step.observation.position[1], 65, 'never stepped onto the exposed lava')
    assert.equal(kinds(step, 'descended').length, 0)
    assert.equal(kinds(step, 'exposed')[0].item, 'lava')
    assert.equal(step.observation.health, 20)
  }
  {
    const s = scene({ blocks: { '1,65,1': 'lava' } })
    const step = await s.stair({ stairs: 1 })
    assert.equal(step.reason, 'observed_hazard', 'lava beside the corridor')
    assert.equal(kinds(step, 'mined').length < 3, true)
  }
  {
    const s = scene({ blocks: { '1,63,0': 'air', '1,62,0': 'air' } })
    const step = await s.stair({ stairs: 1 })
    assert.equal(step.reason, 'unsafe_floor')
    assert.equal(step.observation.position[1], 65)
    assert.equal(step.stable_boundary, true)
  }
  {
    const s = scene({ position: [0.32, 65, 0.5] })
    const step = await s.stair({ stairs: 1 })
    assert.equal(step.reason, 'stairs_completed', 'floor hidden by the ledge needs a nudge, not a blind step')
  }
  {
    const s = scene({ onGround: false })
    const step = await s.stair({ stairs: 1 })
    assert.equal(step.reason, 'stairs_completed', 'reset state has not yet observed the ground')
    assert.equal(kinds(step, 'mined').length, 3)
  }
  {
    const s = scene({ durability: 2 })
    const step = await s.stair({ stairs: 2 })
    assert.equal(step.reason, 'tool_broken')
    assert.equal(step.observation.tool, null)
    assert.equal(kinds(step, 'mined').length, 2)
    assert.equal(kinds(step, 'descended').length, 0)
  }
  {
    const s = scene()
    const step = await s.stair({ stairs: 4 }, 20)
    assert.equal(step.reason, 'macro_tick_limit')
    assert.equal(step.actual_ticks, 20)
    assert.equal(kinds(step, 'stopped').length, 1)
  }
  {
    const s = scene()
    vm.runInContext('activeTicks = budget - 10', s.c)
    const step = await s.stair({ stairs: 4 }, 10)
    assert.equal(step.reason, 'active_tick_limit')
    assert.equal(step.truncated, true)
    assert.equal(step.actual_ticks, 10)
  }
  for (const [label, options, params] of [
    ['too many stairs', {}, { stairs: 5 }], ['diagonal', {}, { direction: [1, 1] }], ['missing direction', {}, { direction: null }],
    ['diamond must stop', {}, { stop_blocks: ['iron_ore'] }], ['stop list is ores only', {}, { stop_blocks: ['diamond_ore', 'stone'] }],
    ['needs a pickaxe', { tool: null }, {}], ['axe is not a pickaxe', { tool: 'iron_axe' }, {}]
  ]) {
    const s = scene(options)
    const step = await s.stair(params)
    assert.equal(step.reason, 'invalid_stair', label)
    assert.equal(step.invalid, true, label)
    assert.equal(step.actual_ticks, 1, label)
    assert.deepEqual(s.dug, [], label)
  }
  {
    // Falling gravel refills the opened cell: only the new observation can reveal that.
    let refilled = false
    const s = scene({ onDig: (point, changed) => {
      if (point.join(',') === '1,65,0' && !refilled) { refilled = true; changed.set('1,66,0', 'gravel') }
    } })
    const step = await s.stair({ stairs: 1 })
    assert.equal(step.reason, 'stairs_completed')
    assert.equal(kinds(step, 'mined').length, 4)
  }
  {
    // A refill above the cell being cut hides it mid-dig (seen in actual Minecraft): start over from the top.
    let ticks = 0
    const s = scene({ digTicks: 6 })
    s.c.afterTick = () => { if (s.dug.length === 2 && ++ticks === 2) s.changed.set('1,65,0', 'gravel') }
    const step = await s.stair({ stairs: 1 })
    assert.equal(step.reason, 'stairs_completed')
    assert.deepEqual(s.dug, [[1, 66, 0], [1, 65, 0], [1, 65, 0], [1, 64, 0]], 'the refilled cell is cut again first')
  }
  for (const [label, maxTicks, start] of [['macro cap', 10, null], ['active budget', 400, 'budget - 10']]) {
    // A refill seen on the cap's last tick ends the macro there; re-judging must not buy one more tick.
    let ticks = 0
    const s = scene({ digTicks: 6 })
    if (start) vm.runInContext(`activeTicks = ${start}`, s.c)
    s.c.afterTick = () => { if (++ticks === 10) s.changed.set('1,65,0', 'gravel') }
    const step = await s.stair({ stairs: 1 }, maxTicks)
    assert.equal(step.actual_ticks, 10, label)
    assert.equal(step.reason, start ? 'active_tick_limit' : 'macro_tick_limit', label)
    assert.equal(vm.runInContext('budget - activeTicks', s.c), start ? 0 : vm.runInContext('budget', s.c) - 10, label)
  }
  {
    // The block is gone from the server view but not yet from memory: retries must spend ticks, not spin.
    const s = scene()
    const blockAt = s.bot.blockAt
    let calls = 0
    s.bot.blockAt = point => {
      const block = blockAt.call(s.bot, point)
      if (point.toArray().join(',') === '1,66,0' && ++calls > 12) return { ...block, name: 'different_block' }
      return block
    }
    const step = await s.stair({ stairs: 1 }, 30)
    assert.ok(step.actual_ticks <= 30)
  }
  {
    const s = scene()
    await s.stair({ stairs: 1 })
    const hold = await s.wait()
    assert.equal(hold.reason, 'wait_completed')
    assert.equal(kinds(hold, 'safe_hold')[0].quantity, 20)
  }
  {
    const s = scene()
    await s.stair({ stairs: 1 })
    let tick = 0
    s.c.afterTick = bot => { if (++tick === 10) bot.health = 19 }
    const hold = await s.wait()
    assert.equal(hold.reason, 'observed_hazard', 'damage during the hold')
    assert.equal(hold.actual_ticks, 10)
    assert.equal(kinds(hold, 'safe_hold').length, 0)
  }
  {
    const s = scene()
    await s.stair({ stairs: 1 })
    const state = await s.observe()
    const cancelled = plain(await s.c.cancelSelection({ candidate_id: 'old', action_kind: 'stair_down', params: {}, max_ticks: 400,
      stop_rule_id: 'stair', source_obs_id: state.obs_id, description: 'stale' }))
    assert.equal(cancelled.cancelled, true)
    assert.equal(kinds(cancelled, 'safe_hold').length, 0, 'a cancellation wait is not a chosen hold')
  }
  process.stdout.write(JSON.stringify({ passed: true }) + '\n')
}

main().catch(error => { console.error(error); process.exitCode = 1 })
