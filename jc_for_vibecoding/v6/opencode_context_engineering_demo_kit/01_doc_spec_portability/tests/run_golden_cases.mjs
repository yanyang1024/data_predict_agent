import fs from 'node:fs'
import { pathToFileURL } from 'node:url'

const modulePath = process.argv[2] || 'generated/pricing.mjs'
const casesPath = process.argv[3] || 'tests/golden_cases.json'
const mod = await import(pathToFileURL(process.cwd() + '/' + modulePath))
const cases = JSON.parse(fs.readFileSync(casesPath, 'utf-8'))

function assertClose(actual, expected, label) {
  if (Math.abs(actual - expected) > 0.001) {
    throw new Error(`${label}: expected ${expected}, got ${actual}`)
  }
}

for (const c of cases) {
  const got = mod.calculateOrderTotal(c.order)
  for (const [key, expected] of Object.entries(c.expected)) {
    assertClose(got[key], expected, `${c.name}.${key}`)
  }
}
console.log(`Golden cases passed: ${cases.length}`)
