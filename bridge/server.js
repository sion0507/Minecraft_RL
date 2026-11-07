// Local administrator lifecycle. Policy requests never receive console access.
const fs = require('node:fs/promises')
const path = require('node:path')
const { spawn } = require('node:child_process')
const { createInterface } = require('node:readline')
const { createHash, randomUUID } = require('node:crypto')
const { once } = require('node:events')

async function treeHash (directory) {
  if (!(await fs.lstat(directory)).isDirectory()) throw new Error('Snapshot root must be a real directory')
  const hash = createHash('sha256')
  async function walk (relative) {
    for (const entry of (await fs.readdir(path.join(directory, relative), { withFileTypes: true })).sort((a, b) => a.name.localeCompare(b.name, 'en'))) {
      const name = path.join(relative, entry.name)
      if (entry.isSymbolicLink()) throw new Error('Snapshot symlink forbidden')
      if (entry.isDirectory()) await walk(name)
      else if (entry.isFile()) {
        const data = await fs.readFile(path.join(directory, name))
        hash.update(JSON.stringify([name, data.length]) + '\n')
        hash.update(data)
      } else throw new Error('Unsupported snapshot entry')
    }
  }
  await walk('')
  return hash.digest('hex')
}

class Server {
  constructor (root) {
    this.root = path.resolve(root)
    this.snapshots = path.resolve(this.root, '../snapshots')
    this.process = null
    this.listeners = new Set()
    this.claimed = false
    this.closed = false
  }

  async runtimeHash () {
    const hash = createHash('sha256')
    for (const name of ['.fabric', 'libraries', 'mods']) {
      hash.update(name + ':' + await treeHash(path.join(this.root, name)))
    }
    for (const name of ['server.jar', 'fabric-server-launch.jar']) {
      hash.update(name + ':')
      hash.update(await fs.readFile(path.join(this.root, name)))
    }
    return hash.digest('hex')
  }

  async claim () {
    if (this.claimed) return
    const installation = JSON.parse(await fs.readFile(path.join(this.root, 'installation.json'), 'utf8'))
    if (installation.minecraft !== '1.16.5' || installation.eula_accepted_by_user !== '2026-11-02') throw new Error('Approved installation required')
    const properties = await fs.readFile(path.join(this.root, 'server.properties'), 'utf8')
    if (!/^server-ip=127\.0\.0\.1$/m.test(properties)) throw new Error('Loopback binding required')
    if (!/^allow-flight=true$/m.test(properties)) throw new Error('Paused server needs allow-flight=true to avoid frozen airborne timeouts')
    this.port = Number(properties.match(/^server-port=(\d+)$/m)?.[1] || 25565)
    if (this.port < 1 || this.port > 65535) throw new Error('Invalid server port')
    // Kernel lease is released on crashes; PID files cannot safely provide that guarantee.
    this.lease = spawn('flock', ['-n', '-F', path.join(this.root, '.mc-diamond-owner'), process.execPath,
      '-e', 'process.stdout.write("locked\\n");process.stdin.resume()'], { stdio: ['pipe', 'pipe', 'ignore'] })
    await new Promise((resolve, reject) => {
      const failed = () => reject(new Error('Server directory already owned or flock unavailable'))
      this.lease.once('error', failed)
      this.lease.once('exit', failed)
      this.lease.stdout.once('data', () => { this.lease.removeListener('exit', failed); resolve() })
    })
    this.claimed = true
  }

  async start () {
    await this.claim()
    if (this.closed) throw new Error('Server lifecycle closed')
    if (this.process) throw new Error('Server already running')
    const child = spawn('java', ['-Xms512M', '-Xmx3G', '-jar', 'fabric-server-launch.jar', 'nogui'], {
      cwd: this.root, stdio: ['pipe', 'pipe', 'pipe']
    })
    this.process = child
    this.initiallyFrozen = false
    const ready = new Promise((resolve, reject) => {
      const timeout = setTimeout(() => reject(new Error('Server startup timeout')), 45000)
      const fail = () => { clearTimeout(timeout); reject(new Error('Server startup failed')) }
      child.once('error', fail)
      child.once('exit', fail)
      this.listeners.add(line => {
        if (line.includes('Done (')) {
          clearTimeout(timeout)
          child.removeListener('error', fail)
          child.removeListener('exit', fail)
          resolve()
        }
      })
    })
    for (const stream of [child.stdout, child.stderr]) {
      createInterface({ input: stream }).on('line', line => {
        if (line.includes('- mc_diamond_pause 1.0.0')) this.initiallyFrozen = true
        // Full administrator output stays in the local server log, not RPC stdout.
        for (const listener of this.listeners) listener(line)
      })
    }
    child.on('exit', () => { if (this.process === child) this.process = null })
    await ready
  }

  async command (text) {
    if (!this.process || this.process.exitCode !== null || /[\r\n]/.test(text)) throw new Error('Server command unavailable')
    const marker = 'mc_' + randomUUID()
    return await new Promise((resolve, reject) => {
      const lines = []
      const child = this.process
      const cleanup = () => { clearTimeout(timeout); this.listeners.delete(receive); child.removeListener('exit', failed) }
      const failed = () => { cleanup(); reject(new Error('Server exited during command')) }
      const receive = line => {
        if (line.includes(marker)) { cleanup(); resolve(lines.join('\n')) } else lines.push(line)
      }
      const timeout = setTimeout(() => { cleanup(); reject(new Error('Server command timeout')) }, 5000)
      this.listeners.add(receive)
      child.once('exit', failed)
      child.stdin.write(text + '\nsay ' + marker + '\n')
    })
  }

  async gameTime () {
    const output = await this.command('time query gametime')
    const match = output.match(/The time is (\d+)/)
    if (!match) throw new Error('Server tick query failed')
    return Number(match[1])
  }

  async step (client, ticks) {
    if (!this.process || this.process.exitCode !== null || !Number.isInteger(ticks) || ticks < 1 || ticks > 400) throw new Error('Server step unavailable')
    const nonce = randomUUID()
    const child = this.process
    return await new Promise((resolve, reject) => {
      let inputSent = false
      const cleanup = () => {
        clearTimeout(timeout)
        client.removeListener('custom_payload', receive)
        client.removeListener('end', failed)
        child.removeListener('exit', failed)
      }
      const failed = () => { cleanup(); reject(new Error('Server/client exited during tick')) }
      const receive = packet => {
        if (packet.channel === 'mcdiamond:step_ready' && !inputSent && packet.data.toString('utf8') === nonce) {
          inputSent = true
          try { client.write('custom_payload', { channel: 'mcdiamond:step_ready', data: Buffer.from(nonce) }) } catch (error) { cleanup(); reject(error) }
          return
        }
        if (packet.channel !== 'mcdiamond:tick' || !inputSent) return
        const fields = packet.data.toString('utf8').split(' ')
        if (fields[0] !== nonce) return
        cleanup()
        const before = Number(fields[1]); const after = Number(fields[2])
        if (fields.length !== 3 || !fields.slice(1).every(s => /^\d+$/.test(s)) ||
          !Number.isSafeInteger(before) || !Number.isSafeInteger(after) || after < before) {
          reject(new Error('Invalid server tick receipt'))
        } else resolve({ before, after })
      }
      const timeout = setTimeout(() => { cleanup(); reject(new Error('Tick step timeout')) }, ticks * 50 + 5000)
      client.on('custom_payload', receive)
      client.once('end', failed)
      child.once('exit', failed)
      child.stdin.write('mcdiamond_step ' + ticks + ' ' + nonce + '\n')
    })
  }

  async stop () {
    const child = this.process
    if (!child) return
    const exited = once(child, 'exit')
    child.stdin.write('stop\n')
    const timeout = setTimeout(() => child.kill('SIGTERM'), 10000)
    try { await exited } finally { clearTimeout(timeout); this.listeners.clear() }
  }

  async saveSnapshot (task, state) {
    if (!['C4', 'G1', 'G2', 'G3', 'G4'].includes(task)) throw new Error('Unknown task')
    const target = path.join(this.snapshots, task)
    await fs.mkdir(this.snapshots, { recursive: true })
    // Never replace a frozen reference snapshot.
    await fs.mkdir(target)
    await fs.cp(path.join(this.root, 'world'), path.join(target, 'world'), { recursive: true, errorOnExist: true, force: false })
    const manifest = { task, ...state, sha256: await treeHash(path.join(target, 'world')) }
    await fs.writeFile(path.join(target, 'snapshot.json'), JSON.stringify(manifest, null, 2) + '\n', { flag: 'wx' })
    return manifest
  }

  async restore (task) {
    if (!['C4', 'G1', 'G2', 'G3', 'G4'].includes(task)) throw new Error('Unknown task')
    await this.claim()
    const source = path.join(this.snapshots, task)
    for (const directory of [this.root, this.snapshots, source, path.join(this.root, 'world')]) {
      if (!(await fs.lstat(directory)).isDirectory()) throw new Error('Symlink directory forbidden')
    }
    const manifest = JSON.parse(await fs.readFile(path.join(source, 'snapshot.json'), 'utf8'))
    if (manifest.task !== task || manifest.sha256 !== await treeHash(path.join(source, 'world'))) throw new Error('Snapshot hash mismatch')
    await this.stop()
    const staged = path.join(this.root, 'world-stage-' + randomUUID())
    await fs.cp(path.join(source, 'world'), staged, { recursive: true, errorOnExist: true, force: false })
    if (manifest.sha256 !== await treeHash(staged)) throw new Error('Restored snapshot hash mismatch')
    // Retain the prior mutable world so an interrupted swap cannot destroy it.
    const previous = path.join(this.root, 'world-previous-' + randomUUID())
    await fs.rename(path.join(this.root, 'world'), previous)
    try { await fs.rename(staged, path.join(this.root, 'world')) } catch (error) { await fs.rename(previous, path.join(this.root, 'world')); throw error }
    await this.start()
    await fs.rm(previous, { recursive: true })
    return manifest
  }

  async close () {
    if (this.closing) return await this.closing
    this.closed = true
    this.closing = (async () => {
      await this.stop()
      if (this.claimed) {
        const released = once(this.lease, 'exit')
        this.lease.stdin.end()
        await released
        this.claimed = false
      }
    })()
    return await this.closing
  }
}

module.exports = { Server, treeHash }
