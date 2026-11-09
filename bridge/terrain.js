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
const FAR_RADIUS = 32 // Decision observations (#44); macro ticks rescan only NEAR_RADIUS for their stop checks.
const NEAR_RADIUS = 8
// Python routes are at most 16 steps (plus head/jump cells), so the policy map carries remembered air only this close.
const AIR_WINDOW = 18
const open = new Set(['air', 'cave_air', 'void_air'])
const fullCube = s => s.length === 6 && s[0] === 0 && s[1] === 0 && s[2] === 0 && s[3] === 1 && s[4] === 1 && s[5] === 1

class Terrain {
  constructor () { this.reset() }

  reset () {
    this.memory = new Map()
    this.version = 0
    this.visited = []
    this.visitKeys = new Set()
    this.visible = new Set()
    this.discoveredOpen = 0 // Positions first observed passable: explore progress that the air window cannot show.
  }

  // Policy map: every remembered non-air cell, remembered air within AIR_WINDOW (Chebyshev) of `position` (all air
  // without one). The executor keeps using the whole memory.
  cells (position = null) {
    const [x, y, z] = position ? position.map(Math.floor) : []
    const near = p => !position || Math.max(Math.abs(p[0] - x), Math.abs(p[1] - y), Math.abs(p[2] - z)) <= AIR_WINDOW
    return [...this.memory.values()].filter(cell => !open.has(cell.block) || near(cell.position))
      .map(cell => ({ ...cell, visible: this.visible.has(key(cell.position)) }))
      .sort((a, b) => a.position[0] - b.position[0] || a.position[1] - b.position[1] || a.position[2] - b.position[2])
  }

  // One ray from the eye to every cell centre within `radius`; a cell is visible when some ray reaches it. Decision
  // observations use FAR_RADIUS, the per-tick checks inside a macro NEAR_RADIUS; `visible` is always the last scan's set.
  scan (bot, radius = FAR_RADIUS) {
    const origin = bot.entity.position.offset(0, bot.entity.eyeHeight, 0).toArray()
    const [bx, by, bz] = origin.map(Math.floor)
    const side = 2 * radius + 5 // Every ray/side cell lies within radius + 2 of the eye's cell.
    const cache = new Uint8Array(side ** 3) // 0 unseen, 1 passable, 2 stops the ray
    let changed = false
    const visible = new Set()
    const inspect = (x, y, z) => {
      const index = ((x - bx + radius + 2) * side + (y - by + radius + 2)) * side + (z - bz + radius + 2)
      if (cache[index]) return cache[index] === 1
      cache[index] = 2
      if (Math.hypot(x + 0.5 - origin[0], y + 0.5 - origin[1], z + 0.5 - origin[2]) > radius) return false
      const block = bot.blockAt(new Vec3(x, y, z), false)
      if (!block) return false
      const id = `${x},${y},${z}`
      visible.add(id)
      const hazard = hazards.has(block.name)
      const passable = block.shapes.length === 0 && !hazard
      const support = !hazard && !slippery.has(block.name) && block.shapes.length === 1 && fullCube(block.shapes[0])
      const old = this.memory.get(id)
      if (!old || old.block !== block.name || old.passable !== passable || old.support !== support || old.hazard !== hazard) {
        if (!old && passable) this.discoveredOpen++
        this.memory.set(id, { block: block.name, position: [x, y, z], passable, support, hazard })
        changed = true
      }
      if (passable) cache[index] = 1
      return passable
    }
    const [ox, oy, oz] = origin
    for (let dx = -radius; dx <= radius; dx++) for (let dy = -radius; dy <= radius; dy++) for (let dz = -radius; dz <= radius; dz++) {
      const [tx, ty, tz] = [bx + dx, by + dy, bz + dz]
      const [ex, ey, ez] = [tx + 0.5 - ox, ty + 0.5 - oy, tz + 0.5 - oz]
      if (Math.hypot(ex, ey, ez) > radius) continue
      const [sx, sy, sz] = [Math.sign(ex), Math.sign(ey), Math.sign(ez)]
      const [rx, ry, rz] = [ex ? 1 / Math.abs(ex) : Infinity, ey ? 1 / Math.abs(ey) : Infinity, ez ? 1 / Math.abs(ez) : Infinity]
      let [px, py, pz] = [bx, by, bz]
      // Ray parameter of the next boundary on each axis, as in a voxel traversal.
      let mx = ex ? (px + (sx > 0 ? 1 : 0) - ox) / ex : Infinity
      let my = ey ? (py + (sy > 0 ? 1 : 0) - oy) / ey : Infinity
      let mz = ez ? (pz + (sz > 0 ? 1 : 0) - oz) / ez : Infinity
      // Each move crosses at least one boundary, so the ray reaches the target within its Manhattan distance.
      for (let n = 0; ; n++) {
        if (n > Math.abs(dx) + Math.abs(dy) + Math.abs(dz)) throw new Error('Ray missed its target cell')
        if (!inspect(px, py, pz) || (px === tx && py === ty && pz === tz)) break
        const next = Math.min(mx, my, mz)
        const [hx, hy, hz] = [Math.abs(mx - next) < 1e-10, Math.abs(my - next) < 1e-10, Math.abs(mz - next) < 1e-10]
        if (hx + hy + hz > 1) {
          // Supercover: never see through the edge/corner where opaque cells touch.
          const axes = [hx && 0, hy && 1, hz && 2].filter(axis => axis !== false)
          let blocked = false
          for (let mask = 1; mask < (1 << axes.length) - 1 && !blocked; mask++) {
            const moved = axis => axes.some((a, i) => a === axis && mask & (1 << i))
            blocked = !inspect(px + (moved(0) ? sx : 0), py + (moved(1) ? sy : 0), pz + (moved(2) ? sz : 0))
          }
          if (blocked) break
        }
        if (hx) { px += sx; mx += rx }
        if (hy) { py += sy; my += ry }
        if (hz) { pz += sz; mz += rz }
      }
    }
    if (changed || visible.size !== this.visible.size || [...visible].some(id => !this.visible.has(id))) this.version++
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

module.exports = { Terrain, FAR_RADIUS, NEAR_RADIUS, AIR_WINDOW }
