// Administrator-only diagnostic loader: capture shipping state before pause/query delays.
const Module = require('node:module')
const fs = require('node:fs')
const path = require('node:path')
const original = Module._extensions['.js']
const bridge = path.resolve(__dirname, '../bridge/minecraft.js')
Module._extensions['.js'] = function (module, filename) {
  if (filename !== bridge) return original(module, filename)
  let source = fs.readFileSync(filename, 'utf8')
  const advance = "const executedTicks = await advance(payload.scene === 'fall' ? 1 : payload.scene === 'fire' ? 25 : 5, payload.scene === 'fall')"
  if (!source.includes(advance)) throw new Error('Clock diagnostic capture seam changed')
  source = source.replace(advance, `const executedTicks = payload.scene === 'drop'
    ? (await advance(1, true)) + (await advance(1, true)) : await advance(1, true)
  const immediateClient = clientState()
  const immediateFurnace = payload.scene === 'furnace' ? bot.blockAt(new Vec3(x + 1,y,z)).getProperties().lit : null
  const immediateDrop = payload.scene === 'drop' ? Object.values(bot.entities).find(e =>
    e.getDroppedItem?.()?.name === 'oak_log' && e.position.distanceTo(new Vec3(x + 1,y + 1,z)) < 3)?.position.toArray() : null
  const serverAir = await data('entity ResearchBot','Air')
  const serverFurnace = payload.scene === 'furnace' ? await data(furnace) : null
  const serverDrop = payload.scene === 'drop' ? vector(await data('entity @e[type=minecraft:item,tag=mc_clock,limit=1]','Pos')) : null
  const immediate_sync = {client_oxygen:immediateClient.oxygen,server_oxygen:Number(serverAir.replace(/s$/,'')),
    client_furnace_lit:immediateFurnace,server_furnace_lit:serverFurnace ? Number(serverFurnace.match(/BurnTime: (-?\\d+)s/)[1]) > 0 : null,
    client_drop:immediateDrop,server_drop:serverDrop}`)
  source = source.replace('return { ...payload, before, after, executed_ticks:',
    'return { immediate_sync, ...payload, before, after, executed_ticks:')
  module._compile(source, filename)
}
