// Policy rays stop at the first occupied shape or hazardous surface.
const { Vec3 } = require('vec3')
const hazards = new Set(['lava', 'water', 'fire', 'soul_fire', 'magma_block', 'cactus', 'sweet_berry_bush', 'campfire', 'soul_campfire'])
// shortcut: ice supports are excluded until braking is calibrated on ice.
const slippery = new Set(['ice', 'packed_ice', 'frosted_ice', 'blue_ice'])
const key = p => p.join(',')

class Terrain {
  constructor () { this.reset() }

  reset () {
    this.memory = new Map()
    this.version = 0
    this.visited = []
    this.visitKeys = new Set()
  }

  cells () { return [...this.memory.values()].sort((a, b) => key(a.position).localeCompare(key(b.position), 'en')) }

  scan (bot) {
    const origin = bot.entity.position.offset(0, bot.entity.eyeHeight, 0).toArray()
    const base = origin.map(Math.floor)
    const cache = new Map()
    let changed = false
    const inspect = point => {
      const id = key(point)
      if (cache.has(id)) return cache.get(id)
      if (Math.hypot(...point.map((v, i) => v + 0.5 - origin[i])) > 8) return false
      const block = bot.blockAt(new Vec3(...point), false)
      if (!block) { cache.set(id, false); return false }
      const passable = block.shapes.length === 0 && !hazards.has(block.name)
      const cell = { block: block.name, position: point, passable,
        support: JSON.stringify(block.shapes) === '[[0,0,0,1,1,1]]' && !hazards.has(block.name) && !slippery.has(block.name),
        hazard: hazards.has(block.name) }
      if (JSON.stringify(this.memory.get(id)) !== JSON.stringify(cell)) {
        this.memory.set(id, cell)
        changed = true
      }
      cache.set(id, passable)
      return passable
    }
    for (let dx = -8; dx <= 8; dx++) for (let dy = -8; dy <= 8; dy++) for (let dz = -8; dz <= 8; dz++) {
      const target = [base[0] + dx, base[1] + dy, base[2] + dz]
      const delta = target.map((v, i) => v + 0.5 - origin[i])
      if (Math.hypot(...delta) > 8) continue
      const point = [...base]
      const step = delta.map(Math.sign)
      const stride = delta.map(v => v ? 1 / Math.abs(v) : Infinity)
      const boundary = point.map((v, i) => delta[i] ? (v + (step[i] > 0 ? 1 : 0) - origin[i]) / delta[i] : Infinity)
      for (let n = 0; n < 32; n++) {
        if (!inspect([...point]) || key(point) === key(target)) break
        const next = Math.min(...boundary)
        const axes = [0, 1, 2].filter(i => Math.abs(boundary[i] - next) < 1e-10)
        // Supercover: never see through the edge/corner where opaque cells touch.
        let blocked = false
        for (let mask = 1; mask < (1 << axes.length) - 1; mask++) {
          const side = [...point]
          axes.forEach((axis, i) => { if (mask & (1 << i)) side[axis] += step[axis] })
          if (!inspect(side)) { blocked = true; break }
        }
        if (blocked) break
        for (const axis of axes) { point[axis] += step[axis]; boundary[axis] += stride[axis] }
      }
    }
    if (changed) this.version++
    const visit = bot.entity.position.floored().toArray()
    if (!this.visitKeys.has(key(visit))) { this.visitKeys.add(key(visit)); this.visited.push(visit) }
  }

  safe (position) {
    const [x, y, z] = position.map(Math.floor)
    const floor = this.memory.get(key([x, y - 1, z]))
    const feet = this.memory.get(key([x, y, z]))
    const head = this.memory.get(key([x, y + 1, z]))
    return !!(floor?.support && !floor.hazard && feet?.passable && !feet.hazard && head?.passable && !head.hazard)
  }

  validPath (position, route) {
    if (!Array.isArray(route) || route.length < 1 || route.length > 16) return false
    let previous = position.map(Math.floor)
    for (const point of route) {
      if (!Array.isArray(point) || point.length !== 3 || !point.every(Number.isFinite) || !this.safe(point)) return false
      const cell = point.map(Math.floor)
      if (point[0] !== cell[0] + 0.5 || point[1] !== cell[1] || point[2] !== cell[2] + 0.5 ||
          cell[1] !== previous[1] || Math.abs(cell[0] - previous[0]) + Math.abs(cell[2] - previous[2]) !== 1) return false
      previous = cell
    }
    return true
  }

  danger (state) {
    if (state.on_fire || state.in_liquid || state.health <= 0 || !this.safe(state.position)) return true
    return [...this.memory.values()].some(c => c.hazard && Math.hypot(c.position[0] + 0.5 - state.position[0], c.position[1] - state.position[1], c.position[2] + 0.5 - state.position[2]) < 1.5)
  }

  stable (state) {
    // Prismarine applies gravity after a ground collision: a resting vy is -0.0784.
    return state.on_ground && !state.in_liquid && !state.on_fire && this.safe(state.position) &&
      Math.hypot(state.velocity[0], state.velocity[2]) < 0.001 && state.velocity[1] >= -0.08 && state.velocity[1] <= 0.001
  }
}

module.exports = { Terrain }
