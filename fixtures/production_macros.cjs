// Shipping dispatch with scripted Mineflayer I/O; never actual Minecraft evidence.
const assert = require('node:assert/strict')
const vm = require('node:vm')
const loadBridge = require('./bridge_harness.cjs')

function setup () {
  const c = loadBridge()
  vm.runInContext(`
    episode={episode_id:'production',attempt_id:'fixture'}; frozen=connected=pauseVerified=true
    const counts={iron_ingot:3,stick:2}
    const state={position:[0.5,64,0.5],velocity:[0,0,0],health:20,oxygen:300,on_fire:false,
      on_ground:true,in_liquid:false,tool:null,tool_durability:null,map_version:1}
    const table={name:'crafting_table',position:new Vec3(1,64,0)}
    terrain.memory.set('1,64,0',{block:'crafting_table',position:[1,64,0],support:true})
    terrain.visible=new Set(['1,64,0']); terrain.danger=()=>false; terrain.stable=()=>true
    let completion=null
    bot={registry:require('minecraft-data')('1.16.5'),
      inventory:{items:()=>Object.entries(counts).map(([name,count])=>({name,count})),emptySlotCount:()=>20},
      blockAt:p=>{assertPublic(p); return table},
      recipesFor:(id,meta,count,table)=>require('prismarine-recipe')('1.16.5').Recipe.find(id,meta),
      craft:async(recipe,n)=>new Promise(resolve=>{completion=()=>{
        for(const d of recipe.delta){const name=bot.registry.items[d.id].name; counts[name]=(counts[name]||0)+d.count*n}
        completion=null; resolve()
      }}),clearControlStates(){},heldItem:null}
    function assertPublic(p){if(!terrain.visible.has(p.toArray().join(',')))throw Error('hidden block read')}
    observation=async()=>({...episode,...state,inventory:{...counts},obs_id:observationId(),active_ticks:activeTicks,
      remaining_ticks:budget-activeTicks,observed_map:terrain.cells(),furnaces:[]})
    advance=async n=>{activeTicks+=n;if(completion)completion();return n}
    pause=async()=>{}
    var candidate=()=>({candidate_id:'craft',action_kind:'craft_batch',params:{item:'iron_pickaxe',quantity:1,table:[1,64,0]},
      max_ticks:400,stop_rule_id:'production_or_hazard',source_obs_id:observationId(),description:'one recipe'})
  `, c)
  return c
}

async function main () {
  const c = setup()
  const result = await c.dispatch({request_id:'craft',method:'step',payload:{candidate:c.candidate()}},false)
  assert.equal(result.invalid,false)
  assert.equal(result.reason,'craft_completed')
  assert.equal(result.observation.inventory.iron_pickaxe,1)
  assert.equal(result.events.filter(e=>e.kind==='crafted'&&e.item==='iron_pickaxe'&&e.quantity===1).length,1)
  assert.ok(result.actual_ticks>=1&&result.actual_ticks<=400)
  // Spending a previously acquired ingredient must not hide its next direct pickup.
  vm.runInContext(`
    counts.iron_ingot=0; acquisitionBaseline={iron_ingot:3}
    awaitDrain=()=>drainEvents()
  `,c)
  c.awaitDrain()
  vm.runInContext(`
    counts.iron_ingot=1
    drops.set(123,{item:'iron_ingot',quantity:1,entity_id:123,position:[1,64,0],collected:true,target:{confirmed:true}})
  `,c)
  assert.equal(c.awaitDrain().filter(e=>e.kind==='acquired').length,1,'pickup after ingredient consumption')
  {
    const c=setup()
    vm.runInContext(`
      counts.oak_log=1;acquisitionBaseline={oak_log:1}
      drops.set(42,{item:'oak_log',quantity:1,entity_id:42,position:[1,64,0],collected:false,target:{confirmed:true}})
      const normalCraft=bot.craft
      bot.craft=async(...args)=>{await normalCraft(...args);counts.oak_log++;drops.get(42).collected=true}
      var simultaneous=candidate();simultaneous.params={item:'oak_planks',quantity:4,table:null}
    `,c)
    const step=await c.dispatch({request_id:'pickup-during-craft',method:'step',payload:{candidate:c.simultaneous}},false)
    assert.equal(step.events.filter(e=>e.kind==='crafted').length,1,'recipe with simultaneous ingredient pickup')
    assert.equal(step.events.filter(e=>e.kind==='acquired'&&e.item==='oak_log').length,1,'pickup during ingredient consumption')
  }
  for (const interrupted of [false,true]) {
    const c=setup()
    c.interrupted=interrupted
    vm.runInContext(`
      counts.oak_log=2
      var batch=candidate();batch.params={item:'oak_planks',quantity:8,table:null}
      if(interrupted){const normalAdvance=advance;advance=async n=>{await normalAdvance(n);state.health=0;return n}}
    `,c)
    const step=await c.dispatch({request_id:'batch',method:'step',payload:{candidate:c.batch}},false)
    assert.equal(step.events.filter(e=>e.kind==='crafted').reduce((n,e)=>n+e.quantity,0),interrupted?4:8)
    assert.equal(step.reason,interrupted?'death':'craft_completed')
  }
  for(const scenario of ['quantity0','quantity9','missing_material','hidden_table']) {
    const c=setup()
    if(scenario==='missing_material')vm.runInContext('counts.iron_ingot=2',c)
    if(scenario==='hidden_table')vm.runInContext("terrain.visible.clear()",c)
    const candidate=c.candidate()
    if(scenario.startsWith('quantity'))candidate.params.quantity=Number(scenario.slice(8))
    const rejected=await c.dispatch({request_id:scenario,method:'step',payload:{candidate}},false)
    assert.equal(rejected.invalid,true,scenario)
    assert.equal(rejected.reason,'invalid_craft',scenario)
    assert.equal(rejected.actual_ticks,1)
    assert.equal(rejected.events.some(e=>e.kind==='crafted'),false)
  }
  for(const scenario of ['place','place_late','load','load_late','load_window','collect','collect_late','collect_window','no_fuel','no_tool','interrupted']) {
    const c=setup()
    c.scenario=scenario
    vm.runInContext(`
      counts.crafting_table=1; counts.iron_ore=3; counts.coal=scenario==='no_fuel'?0:1
      terrain.memory.set('2,64,0',{block:'air',position:[2,64,0],passable:true})
      terrain.memory.set('2,63,0',{block:'stone',position:[2,63,0],support:true})
      terrain.memory.set('-1,64,0',{block:'furnace',position:[-1,64,0],support:true})
      terrain.visible=new Set(['1,64,0','2,64,0','2,63,0','-1,64,0'])
      bot.blockAt=p=>{assertPublic(p);return {name:terrain.memory.get(p.toArray().join(',')).block,position:p}}
      bot.equip=async item=>{bot.heldItem=item;state.tool=item.name}
      bot.placeBlock=async(ref,face)=>{const p=ref.position.plus(face);terrain.memory.get(p.toArray().join(',')).block='crafting_table';
        if(scenario==='place_late'){let delay=2;completion=()=>{if(!--delay){counts.crafting_table--;completion=null}}}else counts.crafting_table--}
      const playerStock=scenario.endsWith('_window')?{...counts}:counts
      const furnace={slots:[null,null,scenario.startsWith('collect')?{name:'iron_ingot',count:3}:null],
        items:()=>Object.entries(playerStock).map(([name,count])=>({name,count})),
        inputItem(){return this.slots[0]},fuelItem(){return this.slots[1]},outputItem(){return this.slots[2]},
        putFuel:async(id,meta,n)=>{furnace.slots[1]={name:'coal',count:n};spend('coal',n)},
        putInput:async(id,meta,n)=>{furnace.slots[0]={name:'iron_ore',count:n};spend('iron_ore',n)}}
      function spend(name,n){
        if(scenario==='load_late'){let delay=2;completion=()=>{if(!--delay){playerStock[name]-=n;completion=null}}}else playerStock[name]-=n
      }
      bot.openFurnace=async()=>{bot.currentWindow=furnace;return furnace}
      bot.closeWindow=()=>{Object.assign(counts,playerStock);bot.currentWindow=null};bot._syncWindow=async()=>{}
      bot.transfer=async options=>{
        const apply=()=>{playerStock.iron_ingot+=options.count;furnace.slots[2].count-=options.count}
        if(scenario==='collect_late'){let delay=2;completion=()=>{if(!--delay){apply();completion=null}}}else apply()
      }
      if(scenario==='interrupted')advance=async n=>{activeTicks+=n;if(completion)completion();state.health=0;return n}
      var selected=candidate()
      if(scenario.startsWith('place'))Object.assign(selected,{action_kind:'place_or_equip',params:{item:'crafting_table',position:[2,64,0],map_version:1}})
      if(scenario.startsWith('load')||scenario==='no_fuel')Object.assign(selected,{action_kind:'furnace_load',params:{position:[-1,64,0],item:'iron_ore',quantity:3,fuel:'coal',fuel_quantity:1,map_version:1}})
      if(scenario.startsWith('collect'))Object.assign(selected,{action_kind:'furnace_collect',params:{position:[-1,64,0],quantity:2,map_version:1}})
      if(scenario==='no_tool'){
        terrain.memory.set('1,64,0',{block:'iron_ore',position:[1,64,0],support:true})
        Object.assign(selected,{action_kind:'mine_visible_cluster',params:{block:'iron_ore',blocks:[[1,64,0]],map_version:1}})
      }
    `,c)
    const step=await c.dispatch({request_id:scenario,method:'step',payload:{candidate:c.selected}},false)
    if(scenario==='no_fuel'||scenario==='no_tool') {
      assert.equal(step.invalid,true,scenario)
      assert.equal(step.events.some(e=>['crafted','furnace_loaded','mined'].includes(e.kind)),false)
    } else if(scenario==='interrupted') {
      assert.equal(step.terminated,true)
      assert.equal(step.reason,'death')
      assert.equal(step.events.filter(e=>e.kind==='crafted').length,1)
    } else {
      assert.equal(step.invalid,false,scenario)
      assert.equal(step.events.some(e=>e.kind===(scenario.startsWith('load')?'furnace_loaded':scenario.startsWith('collect')?'furnace_collected':'placed')),true,scenario)
      if(scenario.startsWith('collect'))assert.equal(step.events.some(e=>e.kind==='smelted'),false,'supplied output is not direct smelting')
      if(scenario.startsWith('load')){
        assert.equal(step.events.filter(e=>e.kind==='furnace_loaded'&&e.item==='iron_ore').reduce((n,e)=>n+e.quantity,0),3)
        vm.runInContext(`furnace.slots=[null,null,{name:'iron_ingot',count:3}];var collect=candidate();
          Object.assign(collect,{action_kind:'furnace_collect',params:{position:[-1,64,0],quantity:2,map_version:1}})`,c)
        const collected=await c.dispatch({request_id:'owned-smelt',method:'step',payload:{candidate:c.collect}},false)
        assert.equal(collected.events.filter(e=>e.kind==='smelted').reduce((n,e)=>n+e.quantity,0),2)
      }
    }
  }
  process.stdout.write(JSON.stringify({passed:true})+'\n')
}
main().catch(error=>{console.error(error);process.exitCode=1})
