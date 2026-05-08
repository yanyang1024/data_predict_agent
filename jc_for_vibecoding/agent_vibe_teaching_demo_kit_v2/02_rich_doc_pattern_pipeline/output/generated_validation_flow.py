#!/usr/bin/env python3
from __future__ import annotations
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'env_package'))
from test_runtime import begin_sequence, end_sequence, drive, expect, wait_cycles, write_bus, set_jitter

def run_all():
    log = []
    begin_sequence(log, 'RESET_STABILITY')
    drive(log, 'rst_n', 0, duration='5ns')
    drive(log, 'rst_n', 1, duration=None)
    expect(log, 'ready', '==', 1, within_cycles=20)
    end_sequence(log, 'RESET_STABILITY')
    begin_sequence(log, 'BURST_WRITE_ACK')
    for i in range(4):
        write_bus(log, 'addr_bus', 'data_bus', 'addr+i', 'data+i')
        expect(log, 'ack', '==', 1, within_cycles=None)
    end_sequence(log, 'BURST_WRITE_ACK')
    begin_sequence(log, 'CLOCK_JITTER_TOLERANCE')
    set_jitter(log, 'clk', 0.25)
    wait_cycles(log, 100)
    expect(log, 'ready', 'stable', True, within_cycles=None)
    end_sequence(log, 'CLOCK_JITTER_TOLERANCE')
    return log

if __name__ == '__main__':
    print(json.dumps(run_all(), indent=2))
