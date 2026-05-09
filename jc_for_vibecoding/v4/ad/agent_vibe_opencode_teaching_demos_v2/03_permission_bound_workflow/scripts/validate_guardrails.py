#!/usr/bin/env python3
import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def run(cmd, expect_ok=True):
    r = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    if expect_ok and r.returncode != 0:
        print(r.stdout); print(r.stderr); raise SystemExit('expected success failed: ' + ' '.join(cmd))
    if not expect_ok and r.returncode == 0:
        raise SystemExit('expected failure succeeded: ' + ' '.join(cmd))
    return r


def main():
    run(['python3','scripts/approved_data_api.py','--metric','latency_ms','--team','alpha','--start-date','2026-05-01','--end-date','2026-05-07','--output','output/query_result.csv'])
    run(['python3','scripts/analysis_cli.py','--input','output/query_result.csv','--output','output/analysis_summary.json','--report','output/permission_report.md'])
    run(['python3','scripts/safe_config_cli.py','get','--key','max_query_days'])
    run(['python3','scripts/approved_data_api.py','--metric','secret_metric','--team','alpha','--start-date','2026-05-01','--end-date','2026-05-07','--output','output/bad.csv'], expect_ok=False)
    run(['python3','scripts/approved_data_api.py','--metric','latency_ms','--team','alpha','--start-date','2026-05-01','--end-date','2026-06-30','--output','output/bad.csv'], expect_ok=False)
    run(['python3','scripts/safe_config_cli.py','set','--key','secret_token','--value','abc'], expect_ok=False)
    print('OK Demo03 guardrails validated: allowed path succeeds, unsafe paths fail.')

if __name__ == '__main__':
    main()
