# Historical Alpha implementation. Use as behavior reference, not as final style.

from alpha_sdk import AlphaTable, AlphaReport


def alpha_run(input_csv, output_json, threshold):
    rows = AlphaTable.read_csv(input_csv)
    kept = []
    for row in rows:
        component = row['component'].strip()
        severity = int(row['severity'])
        if severity >= threshold:
            kept.append({'component': component, 'severity': severity})
    by_component = {}
    for row in kept:
        by_component[row['component']] = by_component.get(row['component'], 0) + 1
    AlphaReport.write_json(output_json, {'threshold': threshold, 'total_retained': len(kept), 'by_component': by_component})
