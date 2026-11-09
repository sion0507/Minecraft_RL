// Policy rays stop at the first occupied shape or hazardous surface.
const { Vec3 } = require('vec3')
const hazards = new Set(['lava', 'water', 'fire', 'soul_fire', 'magma_block', 'cactus', 'sweet_berry_bush', 'campfire', 'soul_campfire'])
// shortcut: ice supports are excluded until braking is calibrated on ice.
const slippery = new Set(['ice', 'packed_ice', 'frosted_ice', 'blue_ice'])
const falling = new Set(['sand', 'red_sand', 'gravel'])
// A landing bounces: a height change from or onto it overruns the 16-block movement cap (#37).
const bouncy = new Set(['slime_block'])
const hazardRadius = 1.5 // No macro starts or continues this close to a remembered hazard (Python HAZARD_RADIUS).
const key = p => p.join(',')

class Terrain {
  constructor () { this.reset() }

  reset () {
    this.memory = new Map()
    this.version = 0
    this.visited = []
    this.visitKeys = new Set()
    this.visible = new Set()
  }

  cells () { return [...this.memory.values()].map(cell => ({ ...cell, visible: this.visible.has(key(cell.position)) })).sort((a, b) => key(a.position).localeCompare(key(b.position), 'en')) }

  scan (bot) {
    const origin = bot.entity.position.offset(0, bot.entity.eyeHeight, 0).toArray()
    const base = origin.map(Math.floor)
    const cache = new Map()
    let changed = false
    const visible = new Set()
    const inspect = point => {
      const id = key(point)
      if (cache.has(id)) return cache.get(id)
      if (Math.hypot(...point.map((v, i) => v + 0.5 - origin[i])) > 8) return false
      const block = bot.blockAt(new Vec3(...point), false)
      if (!block) { cache.set(id, false); return false }
      visible.add(id)
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
    if (changed || [...visible].sort().join(';') !== [...this.visible].sort().join(';')) this.version++
    this.visible = visible
    const visit = bot.entity.position.floored().toArray()
    if (!this.visitKeys.has(key(visit))) { this.visitKeys.add(key(visit)); this.visited.push(visit) }
  }

  safe (position) {
    const [x, y, z] = position.map(Math.floor)
    const floor = this.memory.get(key([x, y - 1, z]))
    return !!(floor?.support && !floor.hazard && this.clear([x, y, z]) && this.clear([x, y + 1, z]))
  }

  // Own head/feet cells a falling block refilled (top-down) over an observed floor; [] when standing normally or in anything else.
  buried (position) {
    const [x, y, z] = position.map(Math.floor)
    const cells = [[x, y + 1, z], [x, y, z]].map(p => this.memory.get(key(p)))
    const floor = this.memory.get(key([x, y - 1, z]))
    if (!floor?.support || floor.hazard || !cells.every(c => c && (c.passable || falling.has(c.block)))) return []
    return cells.filter(c => !c.passable).map(c => c.position)
  }

  clear (point) {
    const cell = this.memory.get(key(point))
    return !!cell?.passable && !cell.hazard
  }

  // Same rule as Python `observed_routes`: one cell sideways, at most one up or down, over observed cells only.
  canStep (from, to) {
    const [x, y, z] = from.map(Math.floor)
    const [nx, ny, nz] = to.map(Math.floor)
    if (Math.abs(nx - x) + Math.abs(nz - z) !== 1 || Math.abs(ny - y) > 1 || !this.safe(to)) return false
    if (ny === y) return true
    if (!this.safe(from) || [[x, y - 1, z], [nx, ny - 1, nz]].some(p => bouncy.has(this.memory.get(key(p)).block))) return false
    // Down: the head passes the front cell at the start height. Up: the jump lifts the head into the cell over the start;
    // a ceiling one higher still lets the feet clear the step (3-high climbs, checked in the physics fixture).
    return this.clear(ny < y ? [nx, y + 1, nz] : [x, y + 2, z])
  }

  // The one open cell a step crosses: over the start column on the way up, over the target column on the way down.
  transit (from, to) {
    const [x, y, z] = from.map(Math.floor)
    const [nx, ny, nz] = to.map(Math.floor)
    return ny > y ? key([x, y + 1, z]) : ny < y ? key([nx, y, nz]) : null
  }

  // A point inside the hazard radius is allowed only farther from the hazard than the point before it (Python
  // `observed_routes` is the same rule): walks never enter the radius, and one that starts inside it only moves away.
  validPath (position, route) {
    if (!Array.isArray(route) || route.length < 1 || route.length > 16) return false
    let previous = position.map(Math.floor)
    let near = this.hazardDistance(position)
    for (const point of route) {
      if (!Array.isArray(point) || point.length !== 3 || !point.every(Number.isFinite)) return false
      const cell = point.map(Math.floor)
      if (point[0] !== cell[0] + 0.5 || point[1] !== cell[1] || point[2] !== cell[2] + 0.5 || !this.canStep(previous, cell)) return false
      const away = this.hazardDistance(point)
      if (away < hazardRadius && away <= near) return false
      previous = cell
      near = away
    }
    return true
  }

  // Distance from a position to the nearest remembered hazard; Infinity when none. Memory only.
  hazardDistance (position) {
    let nearest = Infinity
    for (const c of this.memory.values()) {
      if (c.hazard) nearest = Math.min(nearest, Math.hypot(c.position[0] + 0.5 - position[0], c.position[1] - position[1], c.position[2] + 0.5 - position[2]))
    }
    return nearest
  }

  // On the ground over an edge: the centre's cell is open (feet and head clear) and an observed safe cell under the
  // body's footprint (half-width 0.3) holds it up. Natural G2 (#37 run 3): a stair overshot onto such a ledge.
  supported (state) {
    const [px, py, pz] = state.position
    const y = Math.floor(py)
    const [cx, cz] = [Math.floor(px), Math.floor(pz)]
    if (!state.on_ground || !this.clear([cx, y, cz]) || !this.clear([cx, y + 1, cz])) return false
    return [px - 0.3, px + 0.3].some(x => [pz - 0.3, pz + 0.3].some(z => this.safe([Math.floor(x), y, Math.floor(z)])))
  }

  // `transit` is the one open cell a committed stair or step crosses before landing on its observed floor.
  // `floor` lowers the hazard radius for an escape walk: it may continue while no closer than where it began.
  danger (state, transit = null, floor = hazardRadius) {
    const standing = this.safe(state.position) || key(state.position.map(Math.floor)) === transit || this.supported(state)
    if (state.on_fire || state.in_liquid || state.health <= 0 || !standing) return true
    return this.hazardDistance(state.position) < Math.min(hazardRadius, floor)
  }

  // Remembered hazard touching any planned cell. Memory only: never a peek past a surface.
  hazardNear (cells) {
    return [...this.memory.values()].find(c => c.hazard && cells.some(p => p.every((v, i) => Math.abs(v - c.position[i]) <= 1)))
  }

  stable (state) {
    // Prismarine applies gravity after a ground collision: a resting vy is -0.0784.
    return state.on_ground && !state.in_liquid && !state.on_fire && this.safe(state.position) &&
      Math.hypot(state.velocity[0], state.velocity[2]) < 0.001 && state.velocity[1] >= -0.08 && state.velocity[1] <= 0.001
  }
}

module.exports = { Terrain }
