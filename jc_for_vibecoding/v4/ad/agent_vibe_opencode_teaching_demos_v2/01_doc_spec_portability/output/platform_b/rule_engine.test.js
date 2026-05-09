const assert = require('assert');
const { classify } = require('./rule_engine');
const cases = require('../../tests/platform_b_cases.json');
for (const c of cases) {
  assert.deepStrictEqual(classify(c.ticket), c.expected, c.name);
}
console.log('OK platform B cases passed:', cases.length);
