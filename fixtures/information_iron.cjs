// Shipping administrator setup with scripted console I/O; not actual Minecraft.
const assert = require('node:assert/strict')
const vm = require('node:vm')
const loadBridge = require('./bridge_harness.cjs')

async function main () {
  for (const scope of ['iron', 'production_no_tool']) {
    const c = loadBridge({ scope })
    vm.runInContext(`
      const cells = new Map()
      reset = async () => {}
      server.command = async command => {
        const parts = command.split(' ')
        if (parts[0] === 'fill') {
          const [x,y,z,a,b,d] = parts.slice(1,7).map(Number)
          for (let i=x;i<=a;i++) for(let j=y;j<=b;j++) for(let k=z;k<=d;k++) {
            const block=parts[7].replace('minecraft:','')
            cells.set([i,j,k].join(','),{block,position:[i,j,k],passable:block==='air',support:block!=='air',hazard:false})
          }
        }
        return 'fixture_target_ok fixture_wall_ok'
      }
      bot={entity:{position:new Vec3(0.5,100,0.5)},look:async()=>{}}
      advance=async n=>n;pause=async()=>{}
      var pickupPath=()=>{
        terrain.memory=new Map(cells)
        terrain.memory.set('1,100,0',{block:'air',position:[1,100,0],passable:true})
        return terrain.validPath([0.5,100,0.5],[[1.5,100,0.5]])
      }
    `, c)
    await c.informationFixture({ variant: 'ore', exposed: false, scope })
    if (scope === 'iron') assert.equal(c.pickupPath(), true, 'iron audit must reach its naturally scattered drop after mining')
    else assert.equal(c.pickupPath(), false, 'no-tool boundary fixture keeps its existing three-block column')
  }
  process.stdout.write(JSON.stringify({ passed: true }) + '\n')
}
main().catch(error => { console.error(error); process.exitCode = 1 })
