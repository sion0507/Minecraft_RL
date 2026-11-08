// Shipping drop attribution and administrator log over scripted Mineflayer events; never Minecraft evidence.
const assert = require('node:assert/strict')
const vm = require('node:vm')
const { EventEmitter } = require('node:events')
const loadBridge = require('./bridge_harness.cjs')

async function connected () {
  const c = loadBridge({ EventEmitter })
  const mineflayer = require('../bridge/node_modules/mineflayer')
  const original = mineflayer.createBot
  vm.runInContext(`
    var held = {}
    mineflayer.createBot = () => {
      const b = new EventEmitter()
      b.entity = { id: 1 }
      b.inventory = { items: () => Object.entries(held).map(([name, count]) => ({ name, count })) }
      setTimeout(() => b.emit('spawn'), 0)
      return b
    }
  `, c)
  try { await c.connect() } finally { mineflayer.createBot = original }
  vm.runInContext(`
    activeTicks = 100; acquisitionBaseline = {}; drops.clear(); pendingEvents = []; minedTargets = []
    var target = (block, x) => { const t = { block, position: [x, 64, 0], tick: 100, confirmed: true,
      record: { block, drop_item: null, drop_entity_id: null, acquired_event_id: null } }; minedTargets.push(t); return t }
    var item = (id, name, x, count = 1) => ({ id, position: new Vec3(x + 0.5, 64.5, 0.5), getDroppedItem: () => ({ name, count }) })
  `, c)
  return c
}

const acquired = events => JSON.parse(JSON.stringify(events)).filter(e => e.kind === 'acquired').map(e => [e.item, e.quantity, e.entity_id])

async function main () {
  {
    // diamond_ore drops a diamond: the record links the break to that drop and its acquired event.
    const c = await connected()
    vm.runInContext(`
      var ore = target('diamond_ore', 1); var gem = item(7, 'diamond', 1)
      bot.emit('itemDrop', gem); held.diamond = 1; bot.emit('playerCollect', bot.entity, gem)
    `, c)
    const events = c.drainEvents()
    assert.deepEqual(acquired(events), [['diamond', 1, 7]])
    const record = vm.runInContext('ore.record', c)
    assert.equal(record.drop_item, 'diamond')
    assert.equal(record.drop_entity_id, 7)
    assert.equal(record.acquired_event_id, events[0].event_id)
    assert.equal(record.inventory_after, 1)
  }
  {
    // Two tracked iron drops merge: one pickup of 2 credits both, each record pointing at the same event.
    const c = await connected()
    vm.runInContext(`
      var a = target('iron_ore', 1); var b = target('iron_ore', 2)
      var dropA = item(10, 'iron_ore', 1); var dropB = item(11, 'iron_ore', 2)
      bot.emit('itemDrop', dropA); bot.emit('itemDrop', dropB)
      bot.emit('entityGone', dropA)
      held.iron_ore = 2; bot.emit('playerCollect', bot.entity, item(11, 'iron_ore', 2, 2))
    `, c)
    const events = c.drainEvents()
    assert.deepEqual(acquired(events), [['iron_ore', 2, 11]])
    assert.equal(vm.runInContext('a.record.acquired_event_id', c), events[0].event_id)
    assert.equal(vm.runInContext('b.record.acquired_event_id', c), events[0].event_id)
    assert.equal(vm.runInContext('drops.size', c), 0)
  }
  {
    // An untracked stack merged into a tracked drop never inflates the credit.
    const c = await connected()
    vm.runInContext(`
      target('iron_ore', 1); var dropB = item(11, 'iron_ore', 1)
      bot.emit('itemDrop', dropB)
      held.iron_ore = 3; bot.emit('playerCollect', bot.entity, item(11, 'iron_ore', 1, 3))
    `, c)
    assert.deepEqual(acquired(c.drainEvents()), [['iron_ore', 1, 11]])
  }
  {
    // A given diamond (no break, no tracked drop) and a diamond far from any break are never acquired.
    const c = await connected()
    vm.runInContext(`
      target('diamond_ore', 1); var far = item(20, 'diamond', 9)
      bot.emit('itemDrop', far); held.diamond = 2; bot.emit('playerCollect', bot.entity, far)
    `, c)
    assert.deepEqual(acquired(c.drainEvents()), [])
  }
  {
    // Mining: the iron-tier check is the bridge's; the administrator record keeps server truth before/after.
    const c = loadBridge()
    vm.runInContext(`
      episode = { episode_id: 'diamond', attempt_id: 'fixture' }; frozen = connected = pauseVerified = true; natural = true
      const cell = { block: 'diamond_ore', position: [1, 64, 0], support: true, passable: false, hazard: false }
      terrain.memory.set('1,64,0', cell); terrain.visible = new Set(['1,64,0'])
      terrain.danger = () => false; terrain.stable = () => true; terrain.safe = () => false
      var serverCommands = []
      server.command = async text => { serverCommands.push(text)
        if (text.startsWith('execute if block 1 64 0 minecraft:diamond_ore')) return cell.block === 'diamond_ore' ? 'mc_admin_block_ok' : ''
        if (text.startsWith('execute if block 1 64 0 minecraft:air')) return cell.block === 'air' ? 'mc_admin_block_ok' : ''
        if (text.startsWith('data get entity ResearchBot SelectedItem')) return 'ResearchBot has the following entity data: {id: "minecraft:' + bot.heldItem.name + '", Count: 1b}'
        return '' }
      bot = { entity: { position: new Vec3(0.5, 64, 0.5), eyeHeight: 1.62 }, inventory: { items: () => [] }, clearControlStates () {},
        lookAt: async () => {}, swingArm () {}, digTime: () => 400, heldItem: { name: 'iron_pickaxe', maxDurability: 250, durabilityUsed: 0 },
        blockAt (p) { if (p.toString() !== '(1, 64, 0)') throw Error('hidden query'); return { position: p, name: cell.block } },
        _client: { write (name, packet) { if (packet.status === 2) cell.block = 'air' } } }
      observation = async () => ({ ...episode, obs_id: observationId(), active_ticks: activeTicks, remaining_ticks: budget - activeTicks,
        position: [0.5, 64, 0.5], velocity: [0, 0, 0], health: 20, oxygen: 300, on_fire: false, on_ground: true, in_liquid: false,
        inventory: {}, tool: bot.heldItem?.name ?? null, tool_durability: 250, map_version: 1, observed_map: terrain.cells(), drops: [], furnaces: [] })
      advance = async n => { activeTicks += n; return n }
      pause = async () => {}
      var mine = () => ({ candidate_id: 'mine', action_kind: 'mine_visible_cluster', max_ticks: 400, stop_rule_id: 'wood_or_hazard',
        source_obs_id: observationId(), description: 'diamond', params: { block: 'diamond_ore', blocks: [[1, 64, 0]], map_version: 1 } })
    `, c)
    vm.runInContext("bot.heldItem.name = 'stone_pickaxe'", c)
    const refused = await c.dispatch({ request_id: 'stone', method: 'step', payload: { candidate: c.mine() } }, false)
    assert.equal(refused.reason, 'invalid_cluster', 'a stone pickaxe cannot mine diamond')
    assert.equal(vm.runInContext('verification.length', c), 0)
    vm.runInContext("bot.heldItem.name = 'iron_pickaxe'", c)
    const step = await c.dispatch({ request_id: 'iron', method: 'step', payload: { candidate: c.mine() } }, false)
    assert.equal(step.events.filter(e => e.kind === 'mined' && e.item === 'diamond_ore').length, 1)
    const record = vm.runInContext('verification[0]', c)
    assert.equal(record.natural, true)
    assert.equal(record.server_block_before, true)
    assert.equal(record.server_air_after, true)
    assert.equal(record.server_tool, 'iron_pickaxe')
    assert.equal(record.client_tool, 'iron_pickaxe')
    assert.equal(JSON.stringify(step.observation).includes('server_'), false, 'administrator evidence stays out of the observation')
    assert.equal(await c.dispatch({ request_id: 'log', method: 'verification_log', payload: {} }, false).catch(e => e.code), 'permission_denied')
    const log = await c.dispatch({ request_id: 'log', method: 'verification_log', payload: {} }, true)
    assert.equal(log.records.length, 1)
    assert.equal(log.natural, true)
  }
  process.stdout.write(JSON.stringify({ passed: true }) + '\n')
}

main().catch(error => { console.error(error); process.exitCode = 1 })
