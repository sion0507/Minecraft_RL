// Scripted physics contract; this does not run or certify a Minecraft server.
const vm = require('node:vm')
const loadBridge = require('./bridge_harness.cjs')
const { Physics, PlayerState } = require('../bridge/node_modules/prismarine-physics')
const { Vec3 } = require('../bridge/node_modules/vec3')
const data = require('../bridge/node_modules/minecraft-data')('1.16.5')
const Block = require('../bridge/node_modules/prismarine-block')('1.16.5')

// Step scenes (#37): the floor changes by `rise` from column `edge` on; the path climbs or drops there. Cells are
// 'x,y,z' keys: `blocks` replace world blocks, `forget` drops a remembered cell, `later` changes blocks after the scan.
const STEPS = {
  step_up: { rise: 1, edge: 1, cells: 2 }, step_down: { rise: -1, edge: 1, cells: 2 },
  step_two_up: { rise: 2, edge: 1, cells: 2 }, step_two_down: { rise: -2, edge: 1, cells: 2 },
  step_unknown: { rise: 1, edge: 1, cells: 2, forget: '0,66,0' }, // The jump's head cell over the start is unseen.
  step_blocked: { rise: 1, edge: 1, cells: 2, blocks: { '0,66,0': 'stone' } }, // ... or seen solid.
  step_low: { rise: 1, edge: 1, cells: 2, blocks: { '0,67,0': 'stone', '1,67,0': 'stone', '2,67,0': 'stone' } }, // 3-high climb.
  step_magma: { rise: -1, edge: 1, cells: 2, blocks: { '1,62,0': 'magma_block' } },
  step_hazard: { rise: -1, edge: 1, cells: 2, blocks: { '1,63,1': 'lava' } },
  step_late_up: { rise: 1, edge: 14, cells: 16 }, step_late_down: { rise: -1, edge: 14, cells: 16 },
  step_edge_down: { rise: -1, edge: 13, cells: 16, start: 0.8 }, // 12 blocks are reached with the body over the edge.
  step_slime: { rise: -1, edge: 13, cells: 16, floor: 'slime_block' },
  step_pit: { rise: -1, edge: 1, cells: 2, later: { '1,62,0': 'air' } } // The remembered landing floor is gone.
}
// Late steps around the 12-block rule, from several start offsets: each must settle or complete, never hang on an edge.
const SWEEP = []
for (const rise of [1, -1]) for (let edge = 9; edge <= 16; edge++) for (const start of [0.3, 0.5, 0.6, 0.7, 0.8, 0.95]) {
  SWEEP.push(`sweep_${rise}_${edge}_${start}`)
  STEPS[SWEEP.at(-1)] = { rise, edge, cells: 16, start }
}

async function run (floorName, invalid = false) {
  const step = STEPS[floorName] ?? { rise: 0, edge: Infinity, cells: 16, floor: floorName }
  const height = x => 64 + (x >= step.edge ? step.rise : 0)
  let changed = {}
  const world = { getBlock (position) {
    const cell = position.floored().toArray().join(',')
    const name = changed[cell] ?? step.blocks?.[cell] ?? (position.y < height(Math.floor(position.x)) ? step.floor ?? 'stone' : 'air')
    const block = new Block(data.blocksByName[name].id, 0, 0)
    block.position = position.floored()
    return block
  } }
  const control = { forward: false, back: false, left: false, right: false, jump: false, sprint: false, sneak: false }
  const bot = {
    entity: { position: new Vec3(step.start ?? 0.5, 64, 0.5), velocity: new Vec3(invalid ? 0.1 : 0, -0.0784, 0),
      onGround: true, yaw: -Math.PI / 2, pitch: 0, effects: {} },
    jumpTicks: 0, jumpQueued: false, fireworkRocketDuration: 0, version: '1.16.5', inventory: { slots: [], items: () => [] },
    setControlState (name, value) { control[name] = value },
    async lookAt (point) { const delta = point.minus(this.entity.position); this.entity.yaw = Math.atan2(-delta.x, -delta.z) },
    blockAt (point) { return world.getBlock(point) }
  }
  const physics = Physics(data, world)
  const context = loadBridge({ fixtureBot: bot })
  const terrain = vm.runInContext('terrain', context)
  // Remember only cells seen during earlier visits along this flat corridor.
  for (const x of [0.5, 8.5, 16.5]) terrain.scan({ entity: { position: new Vec3(x, height(x), 0.5), eyeHeight: 1.62 }, blockAt: bot.blockAt })
  if (step.forget) terrain.memory.delete(step.forget)
  changed = step.later ?? {}
  vm.runInContext('bot = fixtureBot; pauseVerified = true; pause = async () => {}', context)
  context.observation = async () => ({ position: bot.entity.position.toArray(), velocity: bot.entity.velocity.toArray(),
    on_ground: bot.entity.onGround, in_liquid: false, on_fire: false, health: 20,
    map_version: terrain.version, obs_id: String(vm.runInContext('observationIndex', context)) })
  context.advance = async () => {
    physics.simulatePlayer(new PlayerState(bot, control), world).apply(bot)
    for (const name of Object.keys(control)) control[name] = false
    vm.runInContext('activeTicks++', context)
    return 1
  }
  const result = await context.moveObserved({ params: {
    path: invalid ? [] : Array.from({ length: step.cells }, (_, index) => [index + 1.5, height(index + 1), 0.5]), map_version: terrain.version
  }, max_ticks: 400, source_obs_id: '0' })
  return { floorName, invalid, actual_ticks: result.actual_ticks, reason: result.reason,
    stable_boundary: result.stable_boundary, distance_moved: result.distance_moved,
    displacement: result.observation.position[0] - 0.5, position: result.observation.position, events: result.events }
}

;(async () => {
  const results = []
  if (process.argv[2] === 'steps') {
    for (const name of Object.keys(STEPS)) results.push(await run(name))
    process.stdout.write(JSON.stringify(results) + '\n')
    return
  }
  for (const floor of ['stone', 'ice', 'packed_ice', 'frosted_ice', 'blue_ice', 'slime_block']) results.push(await run(floor))
  results.push(await run('stone', true))
  process.stdout.write(JSON.stringify(results) + '\n')
})().catch(error => { console.error(error); process.exitCode = 1 })
