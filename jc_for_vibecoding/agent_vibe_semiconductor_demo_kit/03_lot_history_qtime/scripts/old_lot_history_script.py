# Synthetic legacy-style script for classroom discussion.
# Problems: hard-coded lot, hard-coded input path, no manifest, no tests.
import csv
from datetime import datetime

LOT_ID = 'LOT1001'
INPUT = 'mock_data/lot_history_sample.csv'

rows = []
with open(INPUT) as f:
    for row in csv.DictReader(f):
        if row['lot_id'] == LOT_ID:
            rows.append(row)
print('rows', len(rows))
for row in rows:
    t1 = datetime.fromisoformat(row['move_in'])
    t2 = datetime.fromisoformat(row['move_out'])
    print(row['step_id'], (t2 - t1).total_seconds() / 3600.0)
