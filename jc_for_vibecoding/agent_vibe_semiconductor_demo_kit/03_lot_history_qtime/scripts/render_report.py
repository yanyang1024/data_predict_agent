#!/usr/bin/env python3
import argparse
import csv
import json
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(description='Render synthetic lot history report')
    ap.add_argument('--summary', required=True)
    ap.add_argument('--manifest', required=True)
    ap.add_argument('--output', required=True)
    args = ap.parse_args()

    summary_path = Path(args.summary)
    manifest = json.loads(Path(args.manifest).read_text(encoding='utf-8'))
    rows = list(csv.DictReader(summary_path.open(encoding='utf-8')))
    flagged = [r for r in rows if str(r['qtime_flag']).lower() == 'true']
    top_q = sorted([r for r in rows if r['qtime_hours'] != ''], key=lambda r: float(r['qtime_hours']), reverse=True)[:3]

    lines = []
    lines.append('# Lot History UT/QTime Report')
    lines.append('')
    lines.append(f"Lot: `{manifest['lot_id']}`")
    lines.append(f"Rows analyzed: {manifest['row_count']}")
    lines.append(f"Time range: {manifest['time_range']['min_move_in']} to {manifest['time_range']['max_move_out']}")
    lines.append('')
    lines.append('## Key Observations')
    if not rows:
        lines.append('- No data returned for this lot.')
    else:
        lines.append(f'- Calculated UT for {len(rows)} route steps.')
        lines.append(f'- Found {len(flagged)} QTime threshold flag(s).')
        for r in flagged:
            lines.append(f"- QTime flag on `{r['step_pair']}`: {r['qtime_hours']} h > threshold {r['qtime_threshold_hours']} h.")
    lines.append('')
    lines.append('## Top QTime Segments')
    for r in top_q:
        lines.append(f"- `{r['step_pair']}`: {r['qtime_hours']} h, equipment `{r['equipment_id']}` / chamber `{r['chamber_id']}`.")
    lines.append('')
    lines.append('## Suggested Next Checks')
    lines.append('- Check tool availability, chamber queue, recipe version, and hold history around flagged intervals.')
    lines.append('- Compare with peer lots using the same product and route if approved data is available.')
    lines.append('- Do not use this report alone for lot hold/release decisions.')
    lines.append('')
    lines.append('## Manifest Warnings')
    if manifest['warnings']:
        for w in manifest['warnings']:
            lines.append(f'- {w}')
    else:
        lines.append('- None')
    lines.append('')
    lines.append('## Safety Note')
    lines.append(manifest['stop_rule_note'])

    Path(args.output).write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'Wrote {args.output}')

if __name__ == '__main__':
    main()
