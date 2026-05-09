def classify(ticket):
    outage = bool(ticket.get('outage', False))
    severity = str(ticket.get('severity', 'low')).lower()
    tier = str(ticket.get('customer_tier', 'standard')).lower()
    age_hours = float(ticket.get('age_hours', 0) or 0)

    if outage is True:
        return {'priority': 'P0', 'route': 'incident-war-room', 'sla_hours': 1}
    if severity == 'high' and tier == 'enterprise':
        return {'priority': 'P1', 'route': 'senior-support', 'sla_hours': 4}
    if severity == 'high':
        return {'priority': 'P2', 'route': 'support', 'sla_hours': 8}
    if age_hours >= 72:
        return {'priority': 'P2', 'route': 'support', 'sla_hours': 8}
    return {'priority': 'P3', 'route': 'support', 'sla_hours': 24}
