// Scripted failure injection, not actual Minecraft pause certification.
const assert = require('node:assert/strict')
const vm = require('node:vm')
const { EventEmitter } = require('node:events')
const loadBridge = require('./bridge_harness.cjs')

async function main () {
  const scenario = process.argv[2]
  const context = loadBridge()
  if (scenario === 'logging') {
    const mineflayer = require('../bridge/node_modules/mineflayer')
    const original = mineflayer.createBot
    mineflayer.createBot = options => {
      // Keep Mineflayer's real error forwarding/logger, without opening a socket.
      const client = new EventEmitter()
      client.wait_connect = true
      client.end = () => {}
      const bot = original({ ...options, client, loadInternalPlugins: false })
      queueMicrotask(() => client.emit('error', new Error('injected connection failure')))
      return bot
    }
    try { await assert.rejects(context.connect(), /Bot disconnected before spawn/) } finally { mineflayer.createBot = original }
  } else {
    context.scenario = scenario
    vm.runInContext(`
      bot = {physicsEnabled: true, clearControlStates () { this.controlsCleared = true }}
      connected = true
      frozen = scenario !== 'freeze_reply'
      pauseVerified = true
      server.command = async () => 'Game runs normally'
      let samples = 0
      sample = async () => ({
        client: {position: [scenario === 'client' ? samples * 0.01 : 0, 64, 0], health: 20},
        server: {position: [0, 64, 0], state: {Air: scenario === 'server' ? String(samples) : '300s'},
          game_ticks: scenario === 'ticks' ? samples++ : (samples++, 0)}
      })
    `, context)
    if (scenario === 'unchanged') await context.pause()
    else await assert.rejects(context.pause(), error => error.code === 'backend_error')
    assert.equal(vm.runInContext('bot.physicsEnabled', context), false)
    assert.equal(vm.runInContext('bot.controlsCleared', context), true)
    if (scenario !== 'unchanged') assert.equal(vm.runInContext('pauseVerified', context), false)
  }
  process.stdout.write(JSON.stringify({ passed: true }) + '\n')
}

main().catch(error => { console.error(error); process.exitCode = 1 })
