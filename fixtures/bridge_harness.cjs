// Load the complete shipping bridge; only its process/pipe entry points are inert.
const fs = require('node:fs')
const vm = require('node:vm')
const path = require('node:path')
const { createRequire } = require('node:module')
const { EventEmitter } = require('node:events')

module.exports = function loadBridge (state = {}) {
  const filename = path.resolve(__dirname, '../bridge/minecraft.js')
  const requireBridge = createRequire(filename)
  class Input extends EventEmitter { destroy () {} close () {} }
  const context = vm.createContext({
    ...state, console, performance, Buffer, setTimeout, clearTimeout,
    __filename: filename, __dirname: path.dirname(filename),
    process: { argv: ['node', filename, '--admin-fd', '3', ...(state.bridgeArgs || [])], version: process.version,
      stdin: new Input(), stdout: process.stdout, stderr: process.stderr, on () {} },
    require (name) {
      if (name === 'node:net') return { Socket: Input }
      if (name === 'node:readline') return { createInterface: () => new Input() }
      return requireBridge(name)
    }
  })
  vm.runInContext(fs.readFileSync(filename, 'utf8'), context, { filename })
  return context
}
