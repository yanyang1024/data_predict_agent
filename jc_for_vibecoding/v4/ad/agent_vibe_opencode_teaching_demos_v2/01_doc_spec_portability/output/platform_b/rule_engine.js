// Auto-generated teaching demo code. Human review required for business semantics.
function classify(ticket) {
  ticket = ticket || {};
  const outage = Boolean(ticket.outage || false);
  const severity = String(ticket.severity || "low").toLowerCase();
  const customerTier = String(ticket.customer_tier || "standard").toLowerCase();
  const ageHours = Number(ticket.age_hours || 0);

  // R1: 中断优先级最高
  if (outage === true) return { priority: 'P0', route: 'incident-war-room', sla_hours: 1 };
  // R2: 企业客户高严重度
  if (severity === "high" && customerTier === "enterprise") return { priority: 'P1', route: 'senior-support', sla_hours: 4 };
  // R3: 一般高严重度
  if (severity === "high") return { priority: 'P2', route: 'support', sla_hours: 8 };
  // R4: 长时间未处理升级
  if (ageHours >= 72) return { priority: 'P2', route: 'support', sla_hours: 8 };
  // R5: 默认规则
  if (true) return { priority: 'P3', route: 'support', sla_hours: 24 };
}

module.exports = { classify };
