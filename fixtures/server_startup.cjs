// Shipping Server.restore with real temporary snapshots and simulated Java/JDK boundaries; not Minecraft evidence.
const assert = require('node:assert/strict')
const fs = require('node:fs/promises')
const sync = require('node:fs')
const path = require('node:path')
const os = require('node:os')
const vm = require('node:vm')
const { EventEmitter } = require('node:events')
const { PassThrough } = require('node:stream')
const { createRequire } = require('node:module')

async function main () {
  const mode = process.argv[2] || 'once'
  const directory = await fs.mkdtemp(path.join(os.tmpdir(), 'mc-startup-'))
  const root = path.join(directory, 'server')
  const source = path.join(directory, 'snapshots/G1/world')
  await fs.mkdir(path.join(root, 'world'), { recursive: true })
  await fs.mkdir(source, { recursive: true })
  await fs.writeFile(path.join(source, 'state'), 'reference snapshot RNG')
  await fs.writeFile(path.join(root, 'world/state'), 'previous mutable world')
  await fs.writeFile(path.join(root, 'installation.json'), JSON.stringify({ minecraft: '1.16.5', eula_accepted_by_user: '2026-11-02' }))
  await fs.writeFile(path.join(root, 'server.properties'), 'server-ip=127.0.0.1\nallow-flight=true\nserver-port=25565\n')
  const java = []
  const kills = []
  const dumps = []
  let freshReady = false
  function exit (child, code = 0, signal = null) {
    child.exitCode = code
    child.signalCode = signal
    child.emit('exit', code, signal)
    if (mode === 'stale-output' && child === java[0] && signal === 'SIGKILL') {
      setTimeout(() => { child.stdout.end('Done (stale child)!\n'); child.stderr.end() }, 8)
    } else {
      child.stdout.end()
      child.stderr.end()
    }
  }
  const subprocess = {
    spawn (command) {
      const child = new EventEmitter()
      Object.assign(child, { pid: 7000 + java.length, exitCode: null, signalCode: null,
        stdin: new PassThrough(), stdout: new PassThrough(), stderr: new PassThrough() })
      child.stdin.on('data', data => { if (data.toString().includes('stop')) exit(child) })
      child.stdin.on('end', () => { if (command === 'flock') exit(child) })
      child.kill = signal => {
        kills.push(signal)
        if (mode !== 'unreaped') exit(child, null, signal)
        return true
      }
      if (command === 'flock') setImmediate(() => child.stdout.write('locked\n'))
      else {
        assert.equal(command, 'java')
        assert.ok(java.every(c => c.exitCode !== null || c.signalCode !== null), 'old Java must be reaped before next spawn')
        assert.equal(sync.readFileSync(path.join(root, 'world/state'), 'utf8'), 'reference snapshot RNG', 'retry restores the same snapshot')
        java.push(child)
        setImmediate(() => {
          if (mode === 'early-exit') { exit(child, 1); return }
          const hangs = mode !== 'normal' && (java.length === 1 || mode === 'twice')
          if (hangs) {
            sync.writeFileSync(path.join(root, 'world/state'), 'partial failed startup mutation')
            child.stdout.write('x'.repeat(90000) + '\nboot stall recent\n')
            child.stderr.write('startup stderr marker\n')
          } else if (mode === 'stale-output') {
            setTimeout(() => {
              if (child.exitCode !== null || child.signalCode !== null) return
              freshReady = true
              child.stdout.write('- mc_diamond_pause 1.0.0\nDone (fresh child)!\n')
            }, 50)
          } else child.stdout.write('- mc_diamond_pause 1.0.0\nDone (0.1s)!\n')
        })
      }
      return child
    },
    execFile (command, args, options, callback) {
      assert.equal(command, 'jstack')
      assert.equal(options.timeout, 5000)
      assert.equal(options.maxBuffer, 1048576)
      dumps.push(Number(args.at(-1)))
      setImmediate(() => callback(mode.startsWith('dump-') ? Error(mode) : null,
        mode.startsWith('dump-') ? '' : 'Full thread dump for ' + args.at(-1), mode.startsWith('dump-') ? 'JDK diagnostic failed' : ''))
    }
  }
  const filename = path.resolve(__dirname, '../bridge/server.js')
  const realRequire = createRequire(filename)
  const context = vm.createContext({ module: { exports: {} }, process, Buffer, console, setImmediate,
    setTimeout: (fn, ms) => setTimeout(fn, ms === 45000 ? (mode === 'stale-output' ? 100 : 20) : ms === 5000 ? 100 : ms), clearTimeout,
    require: name => name === 'node:child_process' ? subprocess : realRequire(name) })
  vm.runInContext(sync.readFileSync(filename, 'utf8'), context, { filename })
  const { Server, treeHash } = context.module.exports
  const hash = await treeHash(source)
  await fs.writeFile(path.join(directory, 'snapshots/G1/snapshot.json'), JSON.stringify({ task: 'G1', sha256: hash }))
  if (mode === 'invalid-snapshot') await fs.writeFile(path.join(source, 'state'), 'changed snapshot')
  if (mode === 'unwritable-log') await fs.mkdir(path.join(root, 'rpc-errors.log'))
  const server = new Server(root)
  try {
    if (mode === 'twice') await assert.rejects(server.restore('G1'), /Server startup timeout/)
    else if (mode === 'unreaped') await assert.rejects(server.restore('G1'), /Server force-kill timeout/)
    else if (mode === 'unwritable-log') await assert.rejects(server.restore('G1'), /EISDIR/)
    else if (mode === 'early-exit') await assert.rejects(server.restore('G1'), /Server startup failed/)
    else if (mode === 'invalid-snapshot') await assert.rejects(server.restore('G1'), /Snapshot hash mismatch/)
    else await server.restore('G1')
    if (mode === 'stale-output') assert.ok(freshReady, 'old Java output must not mark its replacement ready')
    assert.equal(java.length, mode === 'invalid-snapshot' ? 0
      : ['normal', 'early-exit', 'unreaped', 'unwritable-log'].includes(mode) ? 1 : 2)
    assert.equal(server.listeners.size, 0, 'startup listeners cleaned on success and timeout')
    if (!['normal', 'early-exit', 'invalid-snapshot', 'unwritable-log'].includes(mode)) {
      assert.ok(kills.every(signal => signal === 'SIGKILL'))
      assert.equal(kills.length, mode === 'twice' ? 2 : 1)
      const diagnostics = (await fs.readFile(path.join(root, 'rpc-errors.log'), 'utf8')).trim().split('\n').map(JSON.parse)
      const timeouts = diagnostics.filter(r => r.diagnostic === 'server_startup_timeout')
      assert.equal(timeouts.length, mode === 'twice' ? 2 : 1)
      assert.equal(diagnostics.filter(r => r.diagnostic === 'server_startup_retry').length, mode === 'unreaped' ? 0 : 1)
      for (const row of timeouts) {
        assert.ok(row.recent_output.includes('boot stall recent') && row.recent_output.includes('startup stderr marker'))
        assert.ok(row.recent_output.length <= 65536)
        if (mode.startsWith('dump-')) assert.equal(row.jstack.status, 'failed')
        else assert.ok(row.jstack.stdout.includes('Full thread dump for ' + row.pid))
        assert.ok(row.elapsed_ms >= 0 && row.timestamp)
      }
      assert.equal(dumps.length, timeouts.length)
    }
  } finally {
    await server.close()
    assert.ok(java.every(c => c.exitCode !== null || c.signalCode !== null))
    await fs.rm(directory, { recursive: true, force: true })
  }
  console.log(JSON.stringify({ passed: true, mode }))
}
main().catch(error => { console.error(error); process.exitCode = 1 })
