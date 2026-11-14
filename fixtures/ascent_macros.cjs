// Shipping RPC and installed physics; these are mock checks, not Minecraft evidence.
const assert = require('node:assert/strict')
const scene = require('./stair_macros.cjs')

async function step (s, kind, params, ticks = 400) {
  const state = await s.observe()
  return JSON.parse(JSON.stringify(await s.c.dispatch({ request_id: 'ascent', method: 'step', payload: {
    candidate: { candidate_id: 'ascent', action_kind: kind, params: { ...params, map_version: state.map_version },
      max_ticks: ticks, source_obs_id: state.obs_id, stop_rule_id: 'ascent_or_hazard', description: 'ascend' }
  } }, false)))
}

async function main () {
  {
    const blocks = { ...Object.fromEntries(Array.from({ length: 7 }, (_, i) => [`1,${65 + i},0`, 'air'])),
      ...Object.fromEntries(Array.from({ length: 5 }, (_, i) => [`2,${67 + i},0`, 'air'])) }
    const s = scene({ stock: { dirt: 1 }, blocks })
    const result = await step(s, 'move_observed', { path: [[1.5, 65, 0.5], [1.5, 66, 0.5], [2.5, 67, 0.5]],
      scaffold: { item: 'dirt', reserve: 0 } })
    assert.equal(result.reason, 'path_completed', 'a scaffold after walking uses the current near-scan map version')
    assert.equal(result.observation.position[1], 67)
  }
  {
    const stock = { dirt: 1 }
    const s = scene({ stock })
    const place = s.bot.placeBlock
    let remaining = 0
    s.bot.placeBlock = async (...args) => { await place(...args); stock.dirt++; remaining = 2 }
    s.c.afterTick = () => { if (remaining && --remaining === 0) stock.dirt-- }
    const result = await step(s, 'pillar_up', { blocks: 1, item: 'dirt', reserve: 0 })
    assert.equal(result.reason, 'pillar_completed', 'placement inventory updates may need the next active player tick')
    assert.equal(result.observation.inventory.dirt || 0, 0)
  }
  {
    const s = scene()
    const result = await step(s, 'stair_up', { direction: [1, 0], stairs: 2, stop_blocks: ['diamond_ore'] })
    assert.equal(result.reason, 'stairs_completed')
    assert.equal(result.stable_boundary, true)
    assert.equal(result.observation.position[1], 67)
    assert.equal(result.path.length, 2)
  }
  {
    const blocks = Object.fromEntries(Array.from({ length: 5 }, (_, i) => [`1,${67 + i},0`, 'air']))
    const s = scene({ stock: { dirt: 1 }, blocks })
    const result = await step(s, 'move_observed', { path: [[0.5, 66, 0.5], [1.5, 67, 0.5]],
      scaffold: { item: 'dirt', reserve: 0 } })
    assert.equal(result.reason, 'path_completed')
    assert.equal(result.stable_boundary, true)
    assert.equal(result.observation.position[1], 67)
    assert.equal(result.observation.inventory.dirt || 0, 0)
    assert.equal(result.events.filter(e => e.kind === 'placed').length, 1)
  }
  {
    const s = scene({ stock: { dirt: 4 } })
    const result = await step(s, 'pillar_up', { blocks: 4, item: 'dirt', reserve: 0 })
    assert.equal(result.reason, 'pillar_completed')
    assert.equal(result.observation.position[1], 69)
    assert.equal(result.observation.inventory.dirt || 0, 0)
  }
  {
    const s = scene({ stock: { dirt: 4 } })
    const result = await step(s, 'pillar_up', { blocks: 2, item: 'dirt', reserve: 0 })
    assert.equal(result.reason, 'pillar_completed')
    assert.equal(result.stable_boundary, true)
    assert.equal(result.observation.position[1], 67)
    assert.equal(result.observation.inventory.dirt, 2)
    assert.equal(result.events.filter(e => e.kind === 'placed').length, 2)
    assert.ok(result.actual_ticks > 2 && result.actual_ticks <= 400)
    assert.equal(result.observation.health, 20)
  }
  for (const params of [{ blocks: 5, item: 'dirt', reserve: 0 }, { blocks: 2, item: 'dirt', reserve: 0 },
    { blocks: 1, item: 'iron_block', reserve: 0 }, { blocks: 1, item: 'cobblestone', reserve: 3 }]) {
    const s = scene({ stock: { dirt: 1, cobblestone: 3 } })
    const result = await step(s, 'pillar_up', params)
    assert.equal(result.invalid, true)
    assert.equal(result.events.some(e => e.kind === 'placed'), false)
  }
  for (const block of ['stone', 'lava']) {
    const s = scene({ stock: { dirt: 2 }, blocks: { '0,67,0': block } })
    const result = await step(s, 'pillar_up', { blocks: 1, item: 'dirt', reserve: 0 })
    assert.equal(result.events.some(e => e.kind === 'placed'), false)
    assert.equal(result.observation.inventory.dirt, 2)
  }
  for (const falling of ['sand', 'gravel']) {
    const s = scene({ blocks: { '1,67,0': falling } })
    const result = await step(s, 'tunnel', { direction: [1, 0], cells: 1, height: 2, stop_blocks: ['diamond_ore'] })
    assert.equal(result.reason, 'unsafe_cut')
    assert.deepEqual(s.dug, [])
  }
  process.stdout.write(JSON.stringify({ passed: true }) + '\n')
}

main().catch(error => { console.error(error); process.exitCode = 1 })
