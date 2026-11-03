// Scripted physics contract; this does not run or certify a Minecraft server.
const fs = require('node:fs')
const vm = require('node:vm')
const { Physics, PlayerState } = require('../bridge/node_modules/prismarine-physics')
const { Vec3 } = require('../bridge/node_modules/vec3')
const { Terrain } = require('../bridge/terrain')
const data = require('../bridge/node_modules/minecraft-data')('1.16.5')
const Block = require('../bridge/node_modules/prismarine-block')('1.16.5')
const source = fs.readFileSync('bridge/minecraft.js', 'utf8')

async function run (floorName, invalid = false) {
  const world = { getBlock (position) {
    const block = new Block(data.blocksByName[position.y < 64 ? floorName : 'air'].id, 0, 0)
    block.position = position.floored()
    return block
  } }
  const control = { forward: false, back: false, left: false, right: false, jump: false, sprint: false, sneak: false }
  const bot = {
    entity: { position: new Vec3(0.5, 64, 0.5), velocity: new Vec3(invalid ? 0.1 : 0, -0.0784, 0),
      onGround: true, yaw: -Math.PI / 2, pitch: 0, effects: {} },
    jumpTicks: 0, jumpQueued: false, fireworkRocketDuration: 0, version: '1.16.5', inventory: { slots: [] },
    setControlState (name, value) { control[name] = value },
    async lookAt (point) { const delta = point.minus(this.entity.position); this.entity.yaw = Math.atan2(-delta.x, -delta.z) },
    blockAt (point) { return world.getBlock(point) }
  }
  const physics = Physics(data, world)
  const terrain = new Terrain()
  // Remember only cells seen during earlier visits along this flat corridor.
  for (const x of [0.5, 8.5, 16.5]) terrain.scan({ entity: { position: new Vec3(x, 64, 0.5), eyeHeight: 1.62 }, blockAt: bot.blockAt })
  const context = { performance, Math, Vec3, terrain, bot, activeTicks: 0, budget: 36000,
    observationIndex: 0, history: [], pauseVerified: true,
    exactKeys: (value, keys) => Object.keys(value).sort().join(',') === [...keys].sort().join(',') }
  context.observation = async () => ({ position: bot.entity.position.toArray(), velocity: bot.entity.velocity.toArray(),
    on_ground: bot.entity.onGround, in_liquid: false, on_fire: false, health: 20,
    map_version: terrain.version, obs_id: String(context.observationIndex) })
  context.advance = async () => {
    physics.simulatePlayer(new PlayerState(bot, control), world).apply(bot)
    control.forward = false
    context.activeTicks++
    return 1
  }
  // Exercise the shipping function without adding a policy-side test hook to RPC.
  vm.createContext(context)
  vm.runInContext(source.slice(source.indexOf('async function moveObserved'), source.indexOf('async function prepareWorld')), context)
  const result = await context.moveObserved({ params: {
    path: invalid ? [] : Array.from({ length: 16 }, (_, index) => [index + 1.5, 64, 0.5]), map_version: terrain.version
  }, max_ticks: 400, source_obs_id: '0' })
  return { floorName, invalid, actual_ticks: result.actual_ticks, reason: result.reason,
    stable_boundary: result.stable_boundary, distance_moved: result.distance_moved,
    displacement: result.observation.position[0] - 0.5, events: result.events }
}

;(async () => {
  const results = []
  for (const floor of ['stone', 'ice', 'packed_ice', 'frosted_ice', 'blue_ice', 'slime_block']) results.push(await run(floor))
  results.push(await run('stone', true))
  process.stdout.write(JSON.stringify(results) + '\n')
})().catch(error => { console.error(error); process.exitCode = 1 })
