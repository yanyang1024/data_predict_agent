#!/usr/bin/env python3
import argparse, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / 'configs/sandbox_runtime_config.json'
ALLOWED_KEYS = {'max_query_days', 'default_team', 'report_mode'}

def load(): return json.loads(CONFIG.read_text(encoding='utf-8'))
def save(cfg): CONFIG.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    g = sub.add_parser('get'); g.add_argument('--key', required=True)
    s = sub.add_parser('set'); s.add_argument('--key', required=True); s.add_argument('--value', required=True)
    args = ap.parse_args()
    if args.key not in ALLOWED_KEYS:
        raise SystemExit(f'config key not allowed: {args.key}')
    cfg = load()
    if args.cmd == 'get':
        print(json.dumps({args.key: cfg.get(args.key)}, ensure_ascii=False))
    else:
        if args.key == 'max_query_days':
            v = int(args.value)
            if v < 1 or v > 14:
                raise SystemExit('max_query_days must be between 1 and 14')
            cfg[args.key] = v
        else:
            if any(bad in args.value.lower() for bad in ['secret', 'prod', 'production', '../']):
                raise SystemExit('unsafe config value')
            cfg[args.key] = args.value
        save(cfg)
        print(json.dumps({'updated': args.key, 'value': cfg[args.key]}, ensure_ascii=False))

if __name__ == '__main__':
    main()
