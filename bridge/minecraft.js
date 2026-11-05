// Same JSONL wire and administrator FD as the fixture backend; no policy console.
const net = require('node:net')
const fsp = require('node:fs/promises')
const path = require('node:path')
const { createInterface } = require('node:readline')
const { once } = require('node:events')
const { randomUUID, createHash } = require('node:crypto')
const { execFile } = require('node:child_process')
const { promisify, isDeepStrictEqual } = require('node:util')
const { Server } = require('./server')
const mineflayer = require('mineflayer')
const { Vec3 } = require('vec3')
const { Terrain } = require('./terrain')
const terrain = new Terrain()
let history = []

const sleep = ms => new Promise(resolve => setTimeout(resolve, ms))
const identifier = value => typeof value === 'string' && value.length > 0 && value.length <= 128
const exactKeys = (value, keys) => value && !Array.isArray(value) && typeof value === 'object' && Object.keys(value).sort().join(',') === [...keys].sort().join(',')
const fail = code => { const error = new Error(code); error.code = code; throw error }
const scenes = ['flat', 'furnace', 'drop', 'lava', 'fall', 'water', 'fire']
const args = process.argv.slice(2)
const option = (name, fallback) => { const index = args.indexOf(name); return index < 0 ? fallback : args[index + 1] }
const task = option('--task', 'C4')
const server = new Server(option('--server-dir', path.join(__dirname, '../worlds/server')))
let bot = null
let frozen = false
let previousPhysics = true
let episode = null
let activeTicks = 0
let observationIndex = 0
let eventCount = 0
let pendingEvents = []
let minedTargets = []
const drops = new Map()
let acquisitionBaseline = {}
let observationEpoch = randomUUID()
let connected = false
let pauseVerified = false
let clockFingerprint = null
const clockTrials = new Set()
const observationId = () => observationEpoch + ':' + observationIndex
const budget = { C4: 36000, G1: 3600, G2: 12000, G3: 18000, G4: 18000 }[task]

async function fingerprint () {
  const hash = createHash('sha256')
  const java = await promisify(execFile)('java', ['-version'], { timeout: 5000 })
  hash.update(process.version + java.stderr)
  hash.update(await server.runtimeHash())
  for (const file of [__filename, path.join(__dirname, 'server.js'), path.join(__dirname, 'terrain.js'),
    path.join(__dirname, '../src/mc_diamond/clock.py'), path.join(__dirname, 'package-lock.json'),
    ...['C4', 'G1', 'G2', 'G3', 'G4'].map(t => path.join(server.snapshots, t, 'snapshot.json'))]) {
    hash.update(await fsp.readFile(file))
  }
  const properties = (await fsp.readFile(path.join(server.root, 'server.properties'), 'utf8')).split('\n').filter(s => s && !s.startsWith('#')).sort().join('\n')
  hash.update(properties)
  return hash.digest('hex')
}

async function connect () {
  bot = mineflayer.createBot({ host: '127.0.0.1', port: 25565, username: 'ResearchBot', version: '1.16.5', auth: 'offline', physicsEnabled: false, logErrors: false })
  const current = bot
  connected = false
  const lost = () => { connected = false }
  current.on('end', lost)
  current.on('error', lost)
  current.on('error', () => { process.stderr.write('Minecraft bot connection error\n') })
  await new Promise((resolve, reject) => {
    const cleanup = () => { clearTimeout(timeout); current.removeListener('spawn', spawned); current.removeListener('end', ended); current.removeListener('error', ended) }
    const spawned = () => { cleanup(); resolve() }
    const ended = () => { cleanup(); reject(new Error('Bot disconnected before spawn')) }
    const timeout = setTimeout(() => { cleanup(); current.end(); reject(new Error('Bot spawn timeout')) }, 15000)
    current.once('spawn', spawned)
    current.once('end', ended)
    current.once('error', ended)
  })
  connected = true
  current.on('itemDrop', entity => {
    const item = entity.getDroppedItem?.()
    const target = item && minedTargets.find(target => target.block === item.name && target.drop_id === undefined &&
      activeTicks - target.tick <= 2 &&
      entity.position.distanceTo(new Vec3(...target.position).offset(0.5, 0.5, 0.5)) <= 2)
    if (target && !drops.has(entity.id) && item.count === 1) {
      target.drop_id = entity.id
      drops.set(entity.id, { item: item.name, quantity: item.count, entity_id: entity.id,
        position: entity.position.toArray(), collected: false, target })
    }
  })
  current.on('playerCollect', (collector, collected) => {
    eventCount++
    if (collector.id === current.entity.id && drops.has(collected.id)) drops.get(collected.id).collected = true
  })
  await sleep(150)
}

async function disconnect () {
  if (!bot) return
  const current = bot
  bot = null
  connected = false
  const ended = once(current, 'end')
  current.quit()
  await Promise.race([ended, sleep(1000)])
}

async function pause (verifyPosition = false) {
  if (!bot || !connected) fail('backend_error')
  bot.clearControlStates()
  if (!frozen) previousPhysics = bot.physicsEnabled
  bot.physicsEnabled = false
  try {
    if (!frozen) {
      const reply = await server.command('tick freeze deep')
      if (!reply.includes('Game is deeply frozen')) fail('backend_error')
      frozen = true
    }
    await sleep(150)
    const before = await sample()
    await sleep(150)
    const after = await sample()
    if (bot.physicsEnabled || !isDeepStrictEqual(before, after) ||
      (verifyPosition && Math.hypot(...after.client.position.map((value, axis) => value - after.server.position[axis])) > 0.001)) fail('backend_error')
    return after
  } catch (error) {
    pauseVerified = false
    throw error
  }
}

async function data (subject, field = '') {
  const output = await server.command('data get ' + subject + (field ? ' ' + field : ''))
  const match = output.match(/has the following (?:entity|block) data: (.*)/)
  if (!match) throw new Error('State query failed')
  return match[1]
}

function vector (text) {
  const values = text.match(/-?\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?/g)
  if (!values || values.length !== 3) throw new Error('Invalid vector')
  return values.map(Number)
}

function inventory () {
  const result = {}
  for (const item of bot.inventory.items()) result[item.name] = (result[item.name] || 0) + item.count
  return result
}

function clientState () {
  const oxygen = bot.entity.metadata[1]
  if (!Number.isInteger(oxygen)) throw new Error('Oxygen metadata unavailable')
  return { position: [bot.entity.position.x, bot.entity.position.y, bot.entity.position.z],
    velocity: [bot.entity.velocity.x, bot.entity.velocity.y, bot.entity.velocity.z],
    health: bot.health, oxygen: Math.max(0, oxygen), on_fire: !!(bot.entity.metadata[0] & 1),
    on_ground: !!bot.entity.onGround,
    inventory: inventory(), events: eventCount }
}

async function observation () {
  if (!episode || !bot || !connected || !frozen) fail('backend_error')
  const self = clientState()
  terrain.scan(bot)
  const observedDrops = []
  for (const [id, drop] of drops) {
    const entity = bot.entities[id]
    if (!drop.collected && entity) {
      const position = entity.position.toArray()
      const key = position.map(Math.floor).join(',')
      if (terrain.visible.has(key) && terrain.memory.get(key)?.passable) {
        observedDrops.push({ entity_id: id, item: drop.item, quantity: drop.quantity, position })
      }
    }
  }
  return { ...episode, obs_id: observationId(), active_ticks: activeTicks,
    objective_kind: task === 'C4' ? 'full' : 'local', remaining_ticks: Math.max(0, budget - activeTicks),
    position: self.position, velocity: self.velocity, health: self.health, oxygen: self.oxygen,
    on_fire: self.on_fire, on_ground: !!bot.entity.onGround,
    in_liquid: !!(bot.entity.isInWater || bot.entity.isInLava), inventory: self.inventory,
    tool: bot.heldItem ? bot.heldItem.name : null,
    tool_durability: bot.heldItem && bot.heldItem.maxDurability ? bot.heldItem.maxDurability - (bot.heldItem.durabilityUsed || 0) : null,
    yaw: bot.entity.yaw, pitch: bot.entity.pitch, map_version: terrain.version,
    hidden_hazard_peek: false, visited: terrain.visited,
    observed_map: terrain.cells(), drops: observedDrops, history }
}

async function advance (ticks, walking = false) {
  if (!bot || !connected) fail('backend_error')
  if (!Number.isInteger(ticks) || ticks < 1 || ticks > 400 || !frozen) fail('invalid_request')
  const before = await server.gameTime()
  let clientTicks = 0
  const limitPhysics = () => { if (++clientTicks >= ticks) bot.physicsEnabled = false }
  if (walking) bot.on('physicsTick', limitPhysics)
  bot.physicsEnabled = previousPhysics
  try {
    await server.command('tick step ' + ticks)
    const deadline = performance.now() + ticks * 50 + 5000
    let after
    do {
      await sleep(50)
      after = await server.gameTime()
      if (performance.now() > deadline) throw new Error('Tick step timeout')
    } while (after - before < ticks || (walking && bot.health > 0 && clientTicks < ticks))
  } finally {
    if (walking) bot.removeListener('physicsTick', limitPhysics)
    bot.clearControlStates()
    bot.physicsEnabled = false
  }
  if (!walking) await sleep(150)
  const actual = (await server.gameTime()) - before
  activeTicks += actual
  if (actual !== ticks) throw new Error('Unexpected server tick duration')
  return actual
}

async function reset (payload) {
  if (!exactKeys(payload, ['episode_id', 'attempt_id']) || !identifier(payload.episode_id) || !identifier(payload.attempt_id)) fail('invalid_request')
  await disconnect()
  await server.restore(task)
  frozen = server.initiallyFrozen
  await connect()
  await pause()
  previousPhysics = true
  episode = payload
  observationEpoch = randomUUID()
  activeTicks = observationIndex = eventCount = 0
  terrain.reset()
  history = []
  pendingEvents = []
  minedTargets = []
  drops.clear()
  acquisitionBaseline = inventory()
  clockTrials.clear()
  clockFingerprint = await fingerprint()
  const certificate = await fsp.readFile(path.join(server.root, 'clock-verification.json'), 'utf8').then(JSON.parse).catch(() => null)
  pauseVerified = certificate?.fingerprint === clockFingerprint && certificate?.trials === 63 && certificate?.pause_verified === true
  return await observation()
}

async function moveObserved (candidate) {
  const started = performance.now()
  const initial = await observation()
  const route = candidate.params.path
  const allowed = exactKeys(candidate.params, ['path', 'map_version']) &&
    candidate.params.map_version === initial.map_version && terrain.validPath(initial.position, route)
  const limit = Math.min(candidate.max_ticks, budget - activeTicks)
  let ticks = 0
  let index = 0
  let distance = 0
  let idle = 0
  let reason = allowed ? 'path_completed' : 'invalid_path'
  let state = initial
  let interrupted = false
  while (allowed && ticks < limit) {
    if (terrain.danger(state) || state.health < initial.health) { reason = 'observed_hazard'; interrupted = true; break }
    if (index < route.length && Math.hypot(route[index][0] - state.position[0], route[index][2] - state.position[2]) < 0.15) index++
    const settling = index >= route.length || distance >= 15
    if (settling && terrain.stable(state)) { reason = index >= route.length ? 'path_completed' : 'distance_limit'; break }
    if (index < route.length && !terrain.safe(route[index])) { reason = 'path_changed'; interrupted = true; break }
    if (!settling) {
      await bot.lookAt(new Vec3(...route[index]).offset(0, bot.entity.eyeHeight, 0), true)
      bot.setControlState('forward', true)
    }
    const previous = state.position
    ticks += await advance(1, true)
    observationIndex++
    state = await observation()
    const travelled = Math.hypot(...state.position.map((v, i) => v - previous[i]))
    distance += travelled
    idle = travelled < 0.001 && !settling ? idle + 1 : 0
    if (idle >= 20) { reason = 'no_progress'; interrupted = true; break }
  }
  if (!ticks) {
    ticks += await advance(1, true)
    observationIndex++
    state = await observation()
    distance = Math.hypot(...state.position.map((value, axis) => value - initial.position[axis]))
  }
  if (allowed && ticks >= limit) reason = 'active_tick_limit'
  await pause(true)
  history = [...history.slice(-15), 'move_observed:' + reason]
  state = await observation()
  return stepResult(candidate, started, ticks, state,
    [event(distance > 0 ? 'moved' : 'stopped'), ...drainEvents()], reason,
    { invalid: !allowed, stableBoundary: !interrupted && terrain.stable(state), path: allowed ? route : [], distanceMoved: distance })
}

function stepResult (candidate, started, ticks, state, events, reason,
  { invalid = false, stableBoundary = terrain.stable(state) && !terrain.danger(state), path = [], distanceMoved = 0 } = {}) {
  return { observation: state, actual_ticks: ticks, events,
    terminated: state.health <= 0, truncated: state.health > 0 && !invalid && activeTicks >= budget,
    invalid: invalid && state.health > 0, reason, clock_mode: pauseVerified ? 'paused' : 'unverified', pause_verified: pauseVerified,
    stable_boundary: stableBoundary, wall_seconds: (performance.now() - started) / 1000,
    source_obs_id: candidate.source_obs_id, map_version: state.map_version,
    path, stop_evidence: [state.obs_id, reason], distance_moved: distanceMoved }
}

function event (kind, details = {}) {
  return { kind, source: 'minecraft', event_id: observationEpoch + ':event:' + eventCount++, ...details }
}

function drainEvents () {
  const held = drops.size ? inventory() : {}
  for (const [id, drop] of drops) {
    if (drop.target.confirmed && drop.collected && (held[drop.item] || 0) >= (acquisitionBaseline[drop.item] || 0) + drop.quantity) {
      pendingEvents.push(event('acquired', { item: drop.item, quantity: drop.quantity,
        entity_id: drop.entity_id, position: drop.position }))
      acquisitionBaseline[drop.item] = (acquisitionBaseline[drop.item] || 0) + drop.quantity
      drops.delete(id)
    }
  }
  const result = pendingEvents
  pendingEvents = []
  return result
}

function interruptReason (state, initial) {
  if (state.health <= 0) return 'death'
  if (terrain.danger(state) || state.health < initial.health || state.oxygen < initial.oxygen) return 'observed_hazard'
  if (initial.tool && (state.tool !== initial.tool || state.tool_durability === 0)) return 'tool_broken'
  return null
}

async function executeMacro (candidate, recoveryWait = false) {
  const started = performance.now()
  const initial = await observation()
  const limit = Math.min(candidate.max_ticks, budget - activeTicks)
  let state = initial
  let ticks = 0
  let reason = interruptReason(state, initial)
  let invalid = false
  let distance = 0
  let pathTaken = []
  const events = []
  const tick = async () => {
    ticks += await advance(1, true)
    observationIndex++
    state = await observation()
    reason = interruptReason(state, candidate.action_kind === 'place_or_equip' ? { ...initial, tool: null } : initial)
  }
  if (candidate.action_kind === 'wait') {
    const allowed = exactKeys(candidate.params, []) && ([20, 100, 200].includes(candidate.max_ticks) ||
      candidate.max_ticks === Math.min(20, budget - activeTicks) || (recoveryWait && candidate.max_ticks <= 20))
    invalid = !allowed
    if (!allowed) reason = 'invalid_wait'
    while (!reason && ticks < limit) await tick()
    if (!reason) reason = 'wait_completed'
    events.push(event('wait'))
  } else if (candidate.action_kind === 'place_or_equip') {
    const item = exactKeys(candidate.params, ['item']) && bot.inventory.items().find(item =>
      item.name === candidate.params.item && /^(wooden|stone|iron|golden|diamond|netherite)_axe$/.test(item.name))
    if (!reason && item) {
      await bot.equip(item, 'hand')
      events.push(event('equipped', { item: item.name, quantity: 1 }))
      reason = 'equip_completed'
    } else if (!reason) { reason = 'invalid_equipment'; invalid = true }
  } else if (candidate.action_kind === 'mine_visible_cluster') {
    const { blocks, block, map_version: mapVersion } = candidate.params
    const reachable = point => Array.isArray(point) && point.length === 3 && point.every(Number.isInteger) &&
      point[1] >= Math.floor(state.position[1]) && terrain.visible.has(point.join(',')) &&
      terrain.memory.get(point.join(','))?.block === block &&
      Math.hypot(point[0] + 0.5 - state.position[0], point[2] + 0.5 - state.position[2]) <= 1.8 &&
      Math.hypot(point[0] + 0.5 - state.position[0], point[1] + 0.5 - state.position[1] - 1.62, point[2] + 0.5 - state.position[2]) <= 4.5
    const allowed = exactKeys(candidate.params, ['blocks', 'block', 'map_version']) && typeof block === 'string' && /_log$/.test(block) &&
      mapVersion === initial.map_version && Array.isArray(blocks) && blocks.length >= 1 && blocks.length <= 8 &&
      new Set(blocks.map(p => JSON.stringify(p))).size === blocks.length && blocks.every(reachable) &&
      blocks.every((p, i) => i === 0 || blocks.slice(0, i).some(q => p.reduce((sum, v, axis) => sum + Math.abs(v - q[axis]), 0) === 1))
    if (!reason && !allowed) { invalid = true; reason = 'invalid_cluster' }
    const mined = []
    for (const point of allowed ? blocks : []) {
      if (reason || ticks >= limit) break
      if (!reachable(point)) { reason = 'block_changed'; break }
      // Only the selected, currently exposed cell is read. No Mineflayer raycast/neighbour search.
      const target = bot.blockAt(new Vec3(...point), false)
      if (!target || target.name !== block) { reason = 'block_changed'; break }
      const required = Math.ceil(bot.digTime(target) / 50)
      if (!Number.isFinite(required) || required < 1) { reason = 'dig_failed'; break }
      await bot.lookAt(new Vec3(...point).offset(0.5, 0.5, 0.5), true)
      const packet = { location: new Vec3(...point), face: 1 }
      bot._client.write('block_dig', { ...packet, status: 0 })
      try {
        for (let elapsed = 0; elapsed < required && ticks < limit && !reason; elapsed++) {
          bot.swingArm()
          await tick()
          if (!reason && !reachable(point)) reason = 'block_changed'
        }
        if (!reason && ticks < limit) {
          const broken = { block, position: point, tick: activeTicks, confirmed: false }
          minedTargets = minedTargets.filter(target => activeTicks - target.tick <= 2)
          minedTargets.push(broken)
          bot._client.write('block_dig', { ...packet, status: 2 })
          await tick()
          if (terrain.memory.get(point.join(','))?.block === 'air') {
            broken.confirmed = true
            events.push(event('mined', { item: block, quantity: 1, position: point }))
            mined.push(point)
          } else if (!reason) reason = 'dig_failed'
        }
      } finally {
        bot._client.write('block_dig', { ...packet, status: 1 })
      }
    }
    if (!reason && allowed && mined.length < blocks.length) reason = 'macro_tick_limit'
    if (!reason && mined.length) {
      const point = mined.find(p => p[1] === Math.floor(state.position[1]) &&
        terrain.validPath(state.position, [[p[0] + 0.5, p[1], p[2] + 0.5]]))
      if (point && ticks < limit) {
        const route = [[point[0] + 0.5, point[1], point[2] + 0.5]]
        const moved = await moveObserved({ ...candidate, action_kind: 'move_observed',
          source_obs_id: state.obs_id, max_ticks: limit - ticks, params: { path: route, map_version: state.map_version } })
        ticks += moved.actual_ticks
        state = moved.observation
        events.push(...moved.events)
        distance = moved.distance_moved
        pathTaken = route
        if (moved.reason !== 'path_completed') reason = moved.reason
      }
      // Vanilla drop pickup delay is active game time; preserve it inside this macro's cap.
      for (let n = 0; n < 20 && !reason && ticks < limit; n++) await tick()
    }
    if (!reason) reason = 'cluster_completed'
  } else {
    invalid = true
    reason = 'unsupported_action'
  }
  if (!ticks) {
    const outcome = reason
    await tick()
    reason = reason || outcome
  }
  if (!reason || activeTicks >= budget) reason = 'active_tick_limit'
  await pause()
  history = [...history.slice(-15), candidate.action_kind + ':' + reason]
  state = await observation()
  events.push(...drainEvents())
  if (!events.length || !['cluster_completed', 'equip_completed', 'wait_completed'].includes(reason)) events.push(event('stopped'))
  return stepResult(candidate, started, ticks, state, events, reason,
    { invalid, path: pathTaken, distanceMoved: distance })
}

async function cancelSelection (candidate) {
  const result = await executeMacro({ ...candidate, action_kind: 'wait', params: {},
    max_ticks: Math.min(20, candidate.max_ticks) }, true)
  result.cancelled = true
  result.reason = 'candidate_invalidated'
  result.stop_evidence = [result.observation.obs_id, result.reason]
  return result
}

async function prepareWorld () {
  if (await fsp.stat(server.snapshots).catch(() => null)) fail('invalid_request')
  await server.start()
  frozen = server.initiallyFrozen
  await connect()
  const spawn = clientState().position
  const x = Math.floor(spawn[0]); const y = Math.floor(spawn[1]); const z = Math.floor(spawn[2])
  for (const command of ['difficulty peaceful', 'gamemode survival ResearchBot', 'gamerule spawnRadius 0',
    'setworldspawn ' + x + ' ' + y + ' ' + z, 'clear ResearchBot', 'effect clear ResearchBot',
    'effect give ResearchBot minecraft:instant_health 1 10 true', 'effect give ResearchBot minecraft:saturation 1 10 true', 'time set 1000']) await server.command(command)
  await pause()
  await disconnect()
  await server.stop()
  const result = []
  for (const name of ['C4', 'G1']) result.push(await server.saveSnapshot(name, { position: spawn, inventory: {}, preparation: 'natural surface spawn; no ore search' }))
  for (const name of ['G2', 'G3', 'G4']) {
    await server.restore('C4')
    frozen = server.initiallyFrozen
    await connect()
    const tool = name === 'G2' ? 'stone_pickaxe' : 'iron_pickaxe'
    await server.command('give ResearchBot minecraft:' + tool)
    let position = spawn
    if (name === 'G4') {
      // Fixed coordinates chosen independently of ores; preparation is administrator assistance.
      await server.command(`fill ${x - 1} 10 ${z - 1} ${x + 1} 10 ${z + 1} minecraft:stone`)
      await server.command(`fill ${x - 1} 11 ${z - 1} ${x + 1} 13 ${z + 1} minecraft:air`)
      position = [x + 0.5, 11, z + 0.5]
      await server.command('tp ResearchBot ' + position.join(' '))
    }
    await pause()
    await disconnect()
    await server.stop()
    result.push(await server.saveSnapshot(name, { position, inventory: { [tool]: 1 }, preparation: name === 'G4' ? 'fixed chamber at y=11 directly below spawn, administrator carved/provided; no ore search' : 'surface spawn; provided tool; no ore search' }))
  }
  return { snapshots: result, minecraft_verified: true, pause_verified: false }
}

async function sample () {
  const state = {}
  for (const field of ['Pos', 'Motion', 'Health', 'Air', 'Fire', 'Inventory', 'FallDistance', 'HurtTime']) state[field] = await data('entity ResearchBot', field)
  const player = vector(state.Pos)
  delete state.Pos
  return { client: clientState(), server: { position: player, state, game_ticks: await server.gameTime() } }
}

async function clockTrial (payload) {
  if (!exactKeys(payload, ['scene', 'delay_seconds', 'trial']) || !scenes.includes(payload.scene) || ![0, 5, 10].includes(payload.delay_seconds) || ![1, 2, 3].includes(payload.trial)) fail('invalid_request')
  if (!bot) await reset({ episode_id: 'clock', attempt_id: 'clock-1' })
  const manifest = JSON.parse(await fsp.readFile(path.join(server.snapshots, task, 'snapshot.json'), 'utf8'))
  const x = Math.floor(manifest.position[0]); const z = Math.floor(manifest.position[2]); const y = 100
  // These constructed diagnostic scenes are separate from natural task snapshots.
  await server.command(`fill ${x - 2} ${y - 1} ${z - 2} ${x + 2} ${y + 5} ${z + 2} minecraft:air`)
  await server.command(`fill ${x - 2} ${y - 1} ${z - 2} ${x + 2} ${y - 1} ${z + 2} minecraft:stone`)
  await server.command('kill @e[type=minecraft:item,tag=mc_clock]')
  await server.command('clear ResearchBot')
  await server.command('effect clear ResearchBot')
  await server.command('effect give ResearchBot minecraft:instant_health 1 10 true')
  await server.command(`tp ResearchBot ${x + 0.5} ${y} ${z + 0.5}`)
  const furnace = `block ${x + 1} ${y} ${z}`
  if (payload.scene === 'furnace') await server.command(`setblock ${x + 1} ${y} ${z} minecraft:furnace{Items:[{Slot:0b,id:"minecraft:iron_ore",Count:1b},{Slot:1b,id:"minecraft:coal",Count:1b}]}`)
  if (payload.scene === 'drop') await server.command(`summon minecraft:item ${x + 1} ${y + 1} ${z} {Tags:["mc_clock"],Item:{id:"minecraft:oak_log",Count:1b},PickupDelay:40s}`)
  if (payload.scene === 'lava') await server.command(`setblock ${x} ${y} ${z} minecraft:lava`)
  if (payload.scene === 'water') await server.command(`fill ${x - 1} ${y} ${z - 1} ${x + 1} ${y + 3} ${z + 1} minecraft:water`)
  if (payload.scene === 'fire') await server.command(`setblock ${x} ${y} ${z} minecraft:fire`)
  if (payload.scene === 'fall') await server.command(`tp ResearchBot ${x + 0.5} ${y + 4} ${z + 0.5}`)
  const start = performance.now()
  const executedTicks = await advance(payload.scene === 'fall' ? 1 : payload.scene === 'fire' ? 25 : 5)
  await pause()
  const before = await sample()
  if (payload.scene === 'furnace') before.server.furnace = await data(furnace)
  if (payload.scene === 'drop') before.server.drop = await data('entity @e[type=minecraft:item,tag=mc_clock,limit=1]')
  await sleep(payload.delay_seconds * 1000)
  const after = await sample()
  if (payload.scene === 'furnace') after.server.furnace = await data(furnace)
  if (payload.scene === 'drop') after.server.drop = await data('entity @e[type=minecraft:item,tag=mc_clock,limit=1]')
  observationIndex++
  clockTrials.add(JSON.stringify([payload.scene, payload.delay_seconds, payload.trial]))
  return { ...payload, before, after, executed_ticks: executedTicks, wall_seconds: (performance.now() - start) / 1000 }
}

async function informationFixture (payload) {
  if (!(exactKeys(payload, ['variant', 'exposed']) || exactKeys(payload, ['variant', 'exposed', 'scope']) ||
    exactKeys(payload, ['variant', 'exposed', 'scope', 'episode_id', 'attempt_id'])) ||
    !['ore', 'lava'].includes(payload.variant) || typeof payload.exposed !== 'boolean' ||
    (Object.hasOwn(payload, 'scope') && !['wood', 'wood_tool', 'wood_break', 'wood_hazard', 'wood_drop', 'empty'].includes(payload.scope)) ||
    (Object.hasOwn(payload, 'episode_id') && (!identifier(payload.episode_id) || !identifier(payload.attempt_id)))) fail('invalid_request')
  await reset({ episode_id: payload.episode_id || 'information-audit', attempt_id: payload.attempt_id || 'fixture' })
  const x = Math.floor(bot.entity.position.x); const z = Math.floor(bot.entity.position.z); const y = 100
  // Constructed diagnostics only; frozen task snapshots are never edited.
  await server.command(`fill ${x - 9} ${y - 1} ${z - 9} ${x + 9} ${y + 6} ${z + 9} minecraft:air`)
  await server.command(`fill ${x - 9} ${y - 1} ${z - 9} ${x + 9} ${y - 1} ${z + 9} minecraft:stone`)
  await server.command(`fill ${x + 3} ${y} ${z - 8} ${x + 3} ${y + 5} ${z + 8} minecraft:stone`)
  const target = payload.variant === 'ore' ? 'diamond_ore' : 'lava'
  await server.command(`setblock ${x + 4} ${y} ${z} minecraft:${target}`)
  const verified = await server.command(`execute if block ${x + 4} ${y} ${z} minecraft:${target} run say fixture_target_ok`)
  if (!verified.includes('fixture_target_ok')) fail('backend_error')
  if (payload.exposed) await server.command(`fill ${x + 3} ${y} ${z} ${x + 3} ${y + 2} ${z} minecraft:air`)
  else {
    const wall = await server.command(`execute if block ${x + 3} ${y} ${z} minecraft:stone run say fixture_wall_ok`)
    if (!wall.includes('fixture_wall_ok')) fail('backend_error')
  }
  if (payload.scope?.startsWith('wood')) {
    await server.command(`fill ${x + 1} ${y} ${z} ${x + 1} ${y + 1} ${z} minecraft:oak_log`)
    if (['wood_tool', 'wood_break'].includes(payload.scope)) {
      const item = payload.scope === 'wood_break' ? 'wooden_axe{Damage:58}' : 'wooden_axe'
      await server.command(`replaceitem entity ResearchBot inventory.0 minecraft:${item} 1`)
    }
    if (payload.scope === 'wood_hazard') await server.command(`setblock ${x + 1} ${y - 1} ${z} minecraft:lava`)
  }
  if (payload.scope === 'empty') {
    await server.command(`fill ${x - 1} ${y} ${z - 1} ${x + 1} ${y + 2} ${z + 1} minecraft:stone`)
    await server.command(`fill ${x} ${y} ${z} ${x} ${y + 1} ${z} minecraft:air`)
  }
  await server.command(`tp ResearchBot ${x + 0.5} ${y} ${z + 0.5}`)
  await sleep(150)
  await bot.look(0, 0, true)
  let setupTicks = await advance(5, true)
  await pause()
  terrain.reset()
  if (payload.scope === 'wood_drop') {
    const initial = await observation()
    const mined = await executeMacro({ action_kind: 'mine_visible_cluster', params: { block: 'oak_log',
      blocks: [[x + 1, y, z]], map_version: initial.map_version }, max_ticks: 61,
    source_obs_id: initial.obs_id })
    if (!mined.events.some(e => e.kind === 'mined')) fail('backend_error')
    setupTicks += mined.actual_ticks
    // Relocate an owned, actually mined drop; setup assistance is outside episode time.
    const selector = `@e[type=minecraft:item,x=${x + 1},y=${y},z=${z},distance=..3]`
    await server.command(`tp ${selector} ${x + 0.5} ${y} ${z + 0.5}`)
    await server.command(`execute as ${selector} run data merge entity @s {PickupDelay:40s,Motion:[0d,0d,0d]}`)
    setupTicks += await advance(5, true)
    await pause()
    terrain.reset()
  }
  history = []
  activeTicks = observationIndex = 0
  return { fixture_ready: true, setup_ticks: setupTicks }
}

async function dispatch (request, admin) {
  if (!exactKeys(request, ['request_id', 'method', 'payload']) || !identifier(request.request_id) || !request.payload || Array.isArray(request.payload) || typeof request.payload !== 'object') fail('invalid_request')
  const methods = ['reset', 'observe', 'step', 'prepare_world', 'clock_trial', 'certify_clock', 'information_fixture']
  if (!methods.includes(request.method)) fail('invalid_request')
  if (admin ? !['reset', 'prepare_world', 'clock_trial', 'certify_clock', 'information_fixture'].includes(request.method) : !['observe', 'step'].includes(request.method)) fail('permission_denied')
  if (request.method === 'reset') return await reset(request.payload)
  if (request.method === 'clock_trial') return await clockTrial(request.payload)
  if (request.method === 'information_fixture') return await informationFixture(request.payload)
  if (request.method === 'certify_clock') {
    if (!exactKeys(request.payload, []) || clockTrials.size !== 63 || await fingerprint() !== clockFingerprint) fail('invalid_request')
    const certificate = { fingerprint: clockFingerprint, trials: 63, pause_verified: true }
    const temporary = path.join(server.root, 'clock-verification-' + randomUUID() + '.json')
    await fsp.writeFile(temporary, JSON.stringify(certificate) + '\n', { flag: 'wx' })
    await fsp.rename(temporary, path.join(server.root, 'clock-verification.json'))
    pauseVerified = true
    return certificate
  }
  if (request.method === 'prepare_world') { if (!exactKeys(request.payload, [])) fail('invalid_request'); return await prepareWorld() }
  if (request.method === 'observe') { if (!exactKeys(request.payload, [])) fail('invalid_request'); return await observation() }
  if (!exactKeys(request.payload, ['candidate'])) fail('invalid_request')
  const candidate = request.payload.candidate
  if (!exactKeys(candidate, ['candidate_id', 'action_kind', 'params', 'max_ticks', 'stop_rule_id', 'source_obs_id', 'description']) || !identifier(candidate.candidate_id) || !identifier(candidate.stop_rule_id) || typeof candidate.description !== 'string' || !candidate.params || typeof candidate.params !== 'object' || Array.isArray(candidate.params) || !Number.isInteger(candidate.max_ticks) || candidate.max_ticks < 1 || candidate.max_ticks > 400) fail('invalid_request')
  if (!episode || typeof candidate.source_obs_id !== 'string' || !candidate.source_obs_id.startsWith(observationEpoch + ':')) fail('invalid_selection')
  if (activeTicks >= budget) fail('invalid_selection')
  if (candidate.source_obs_id !== observationId()) return await cancelSelection(candidate)
  const current = await observation()
  if (Object.hasOwn(candidate.params, 'map_version') && candidate.params.map_version !== current.map_version) return await cancelSelection(candidate)
  if (candidate.action_kind === 'move_observed') return await moveObserved(candidate)
  return await executeMacro(candidate)
}

let queue = Promise.resolve()
function channel (input, admin) {
  const reader = createInterface({ input })
  reader.on('line', line => {
    queue = queue.then(async () => {
      let id = 'invalid'
      try {
        if (Buffer.byteLength(line) > 1048576) fail('invalid_request')
        const request = JSON.parse(line)
        if (identifier(request?.request_id)) id = request.request_id
        const result = await dispatch(request, admin)
        process.stdout.write(JSON.stringify({ request_id: id, result }) + '\n')
      } catch (error) {
        if (!(error instanceof SyntaxError) && !['invalid_request', 'permission_denied', 'invalid_selection'].includes(error.code)) {
          await fsp.appendFile(path.join(server.root, 'rpc-errors.log'), String(error.stack) + '\n').catch(() => {})
        }
        const code = ['invalid_request', 'permission_denied', 'invalid_selection', 'backend_error'].includes(error.code) ? error.code : 'backend_error'
        process.stderr.write('Minecraft request failed: ' + code + '\n')
        process.stdout.write(JSON.stringify({ request_id: id, error: { code, message: 'Minecraft request failed', retryable: false } }) + '\n')
      }
    })
  })
  return reader
}

const adminFd = Number(option('--admin-fd', '-1'))
if (!Number.isInteger(adminFd) || adminFd < 0 || !budget) throw new Error('Invalid backend configuration')
const adminInput = new net.Socket({ fd: adminFd, readable: true, writable: false })
const administrator = channel(adminInput, true)
const policy = channel(process.stdin, false)
let closing = false
async function close () {
  if (closing) return
  closing = true
  await queue
  await disconnect()
  await server.close()
  administrator.close()
  adminInput.destroy()
  process.exit(0)
}
policy.on('close', () => { close().catch(() => process.exit(1)) })
process.on('SIGTERM', () => {
  // Interrupt in-flight waits/spawn rather than queueing shutdown behind them.
  closing = true
  if (bot) bot.end()
  server.close().then(() => process.exit(0), () => process.exit(1))
})
process.stdout.on('error', error => { if (error.code !== 'EPIPE') throw error })
