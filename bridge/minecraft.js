// Same JSONL wire and administrator FD as the fixture backend; no policy console.
const net = require('node:net')
const fsp = require('node:fs/promises')
const path = require('node:path')
const { createInterface } = require('node:readline')
const { once } = require('node:events')
const { randomUUID, createHash } = require('node:crypto')
const { execFile } = require('node:child_process')
const { promisify } = require('node:util')
const { Server } = require('./server')
const mineflayer = require('mineflayer')

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
  for (const file of [__filename, path.join(__dirname, 'server.js'),
    path.join(__dirname, '../src/mc_diamond/clock.py'), path.join(__dirname, 'package-lock.json'),
    ...['C4', 'G1', 'G2', 'G3', 'G4'].map(t => path.join(server.snapshots, t, 'snapshot.json'))]) {
    hash.update(await fsp.readFile(file))
  }
  const properties = (await fsp.readFile(path.join(server.root, 'server.properties'), 'utf8')).split('\n').filter(s => s && !s.startsWith('#')).sort().join('\n')
  hash.update(properties)
  return hash.digest('hex')
}

async function connect () {
  bot = mineflayer.createBot({ host: '127.0.0.1', port: 25565, username: 'ResearchBot', version: '1.16.5', auth: 'offline', physicsEnabled: false })
  const current = bot
  connected = false
  const lost = () => { connected = false }
  current.on('end', lost)
  current.on('error', lost)
  current.on('error', () => {})
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
  current.on('playerCollect', () => { eventCount++ })
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

async function pause () {
  if (!bot || !connected) fail('backend_error')
  bot.clearControlStates()
  if (!frozen) previousPhysics = bot.physicsEnabled
  bot.physicsEnabled = false
  if (!frozen) { await server.command('tick freeze deep'); frozen = true }
  await sleep(150)
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
  return { ...episode, obs_id: observationId(), active_ticks: activeTicks,
    objective_kind: task === 'C4' ? 'full' : 'local', remaining_ticks: Math.max(0, budget - activeTicks),
    position: self.position, velocity: self.velocity, health: self.health, oxygen: self.oxygen,
    on_fire: self.on_fire, on_ground: !!bot.entity.onGround,
    in_liquid: !!(bot.entity.isInWater || bot.entity.isInLava), inventory: self.inventory,
    tool: bot.heldItem ? bot.heldItem.name : null,
    tool_durability: bot.heldItem && bot.heldItem.maxDurability ? bot.heldItem.maxDurability - (bot.heldItem.durabilityUsed || 0) : null,
    // Terrain observation and non-wait macros are implemented in the following tickets.
    observed_map: [], history: [] }
}

async function advance (ticks) {
  if (!bot || !connected) fail('backend_error')
  if (!Number.isInteger(ticks) || ticks < 1 || ticks > 400 || !frozen) fail('invalid_request')
  const before = await server.gameTime()
  bot.physicsEnabled = previousPhysics
  await server.command('tick step ' + ticks)
  const deadline = performance.now() + ticks * 50 + 5000
  let after
  do {
    await sleep(50)
    after = await server.gameTime()
    if (performance.now() > deadline) throw new Error('Tick step timeout')
  } while (after - before < ticks)
  bot.clearControlStates()
  bot.physicsEnabled = false
  await sleep(150)
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
  clockTrials.clear()
  clockFingerprint = await fingerprint()
  const certificate = await fsp.readFile(path.join(server.root, 'clock-verification.json'), 'utf8').then(JSON.parse).catch(() => null)
  pauseVerified = certificate?.fingerprint === clockFingerprint && certificate?.trials === 63 && certificate?.pause_verified === true
  return await observation()
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

async function dispatch (request, admin) {
  if (!exactKeys(request, ['request_id', 'method', 'payload']) || !identifier(request.request_id) || !exactKeys({ payload: request.payload }, ['payload']) || !request.payload || Array.isArray(request.payload) || typeof request.payload !== 'object') fail('invalid_request')
  const methods = ['reset', 'observe', 'step', 'prepare_world', 'clock_trial', 'certify_clock']
  if (!methods.includes(request.method)) fail('invalid_request')
  if (admin ? !['reset', 'prepare_world', 'clock_trial', 'certify_clock'].includes(request.method) : !['observe', 'step'].includes(request.method)) fail('permission_denied')
  if (request.method === 'reset') return await reset(request.payload)
  if (request.method === 'clock_trial') return await clockTrial(request.payload)
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
  if (!episode || candidate.source_obs_id !== observationId()) fail('invalid_selection')
  const supported = candidate.action_kind === 'wait' && exactKeys(candidate.params, [])
  const started = performance.now()
  const ticks = await advance(Math.min(supported ? candidate.max_ticks : 1, budget - activeTicks))
  observationIndex++
  const next = await observation()
  return { observation: next, actual_ticks: ticks, events: [{ kind: 'wait', source: 'minecraft' }],
    terminated: false, truncated: supported && activeTicks >= budget, invalid: !supported,
    reason: supported ? 'wait_completed' : 'unsupported_action', clock_mode: 'paused',
    // Only the complete real diagnostic can authorize this claim.
    pause_verified: pauseVerified, stable_boundary: next.on_ground && !next.in_liquid,
    wall_seconds: (performance.now() - started) / 1000 }
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
