export function round2(value) {
  return Math.round((value + Number.EPSILON) * 100) / 100
}

export function assertKnown(value, allowed, label) {
  if (!allowed.includes(value)) {
    throw new Error(`unsupported ${label}: ${value}`)
  }
}
