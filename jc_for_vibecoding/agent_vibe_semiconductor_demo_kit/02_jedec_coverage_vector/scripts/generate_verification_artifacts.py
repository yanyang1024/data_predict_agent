#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output'
OUT.mkdir(exist_ok=True)
ENV = json.loads((ROOT / 'env_lib/memory_env.json').read_text(encoding='utf-8'))

COVERAGE = [
    {'id': 'cov_reset_min_2_edges', 'feature': 'reset', 'bins': ['reset_low_2_edges']},
    {'id': 'cov_write_burst_len', 'feature': 'write', 'bins': ['bl4', 'bl8']},
    {'id': 'cov_read_after_write_tw2r', 'feature': 'timing', 'bins': ['tw2r_2_cycles']},
    {'id': 'cov_vdd_corner', 'feature': 'voltage', 'bins': ['low_1080mv', 'nom_1200mv', 'high_1320mv']},
    {'id': 'cov_clock_jitter', 'feature': 'clock', 'bins': ['jitter_minus_5pct', 'jitter_plus_5pct']},
    {'id': 'cov_illegal_we_re_low', 'feature': 'illegal_command', 'bins': ['we0_re0_no_corrupt']},
]

SEQUENCES = [
    {
        'name': 'reset_then_basic_write_read_bl4',
        'purpose': 'Cover reset, write burst length 4, read after write with tW2R.',
        'coverage': ['cov_reset_min_2_edges', 'cov_write_burst_len', 'cov_read_after_write_tw2r'],
        'steps': [
            {'op': 'reset', 'cycles': 2},
            {'op': 'wait_ns', 'value': 5},
            {'op': 'write', 'addr': 16, 'data': 165, 'burst_len': 4},
            {'op': 'wait_cycles', 'value': 2},
            {'op': 'read_expect', 'addr': 16, 'data': 165, 'read_latency': 'needs_designer_confirmation'},
        ]
    },
    {
        'name': 'voltage_sweep_write_bl8',
        'purpose': 'Cover low, nominal, and high voltage corners with burst length 8.',
        'coverage': ['cov_write_burst_len', 'cov_vdd_corner'],
        'steps': [
            {'op': 'set_vdd_mv', 'value': 1080},
            {'op': 'write', 'addr': 32, 'data': 90, 'burst_len': 8},
            {'op': 'set_vdd_mv', 'value': 1200},
            {'op': 'write', 'addr': 33, 'data': 91, 'burst_len': 8},
            {'op': 'set_vdd_mv', 'value': 1320},
            {'op': 'write', 'addr': 34, 'data': 92, 'burst_len': 8},
        ]
    },
    {
        'name': 'illegal_command_no_corrupt',
        'purpose': 'Cover illegal WE_N=0 and RE_N=0 condition and read back prior data.',
        'coverage': ['cov_illegal_we_re_low'],
        'steps': [
            {'op': 'write', 'addr': 48, 'data': 195, 'burst_len': 4},
            {'op': 'illegal_we_re_low', 'addr': 48},
            {'op': 'wait_cycles', 'value': 2},
            {'op': 'read_expect', 'addr': 48, 'data': 195, 'read_latency': 'needs_designer_confirmation'},
        ]
    },
]


def write_coverage_yaml():
    lines = ['coverage_points:']
    for item in COVERAGE:
        lines.append(f'  - id: {item["id"]}')
        lines.append(f'    feature: {item["feature"]}')
        lines.append('    bins:')
        for b in item['bins']:
            lines.append(f'      - {b}')
    (OUT / 'coverage_points.yaml').write_text('\n'.join(lines) + '\n', encoding='utf-8')


def write_sequence_ir():
    obj = {
        'source': 'docs/synthetic_jedec_memory_excerpt.md',
        'environment': 'env_lib/memory_env.json',
        'signals': [s['name'] for s in ENV['signals']],
        'sequences': SEQUENCES,
        'human_review': [
            'Read latency is not defined in the synthetic excerpt.',
            'Voltage corner acceptance criteria require designer confirmation.',
            'Clock jitter injection model is simplified.'
        ]
    }
    (OUT / 'sequence_ir.json').write_text(json.dumps(obj, indent=2), encoding='utf-8')


def sv_value(v):
    if isinstance(v, int):
        return f"8'h{v:02X}" if v <= 255 else str(v)
    return str(v)


def write_sv_sequence():
    lines = ['// Synthetic generated sequence skeleton', 'class generated_mem_sequence extends uvm_sequence;', '  `uvm_object_utils(generated_mem_sequence)', '  task body();']
    for seq in SEQUENCES:
        lines.append(f'    // Sequence: {seq["name"]}')
        for st in seq['steps']:
            op = st['op']
            if op == 'reset':
                lines.append(f'    do_reset({st["cycles"]});')
            elif op == 'wait_ns':
                lines.append(f'    wait_ns({st["value"]});')
            elif op == 'wait_cycles':
                lines.append(f'    wait_cycles({st["value"]});')
            elif op == 'set_vdd_mv':
                lines.append(f'    set_vdd_mv({st["value"]});')
            elif op == 'write':
                lines.append(f'    mem_write(8\'h{st["addr"]:02X}, 8\'h{st["data"]:02X}, {st["burst_len"]});')
            elif op == 'read_expect':
                lines.append(f'    mem_read_expect(8\'h{st["addr"]:02X}, 8\'h{st["data"]:02X}); // latency needs review')
            elif op == 'illegal_we_re_low':
                lines.append(f'    drive_illegal_we_re_low(8\'h{st["addr"]:02X});')
    lines += ['  endtask', 'endclass']
    (OUT / 'generated_sequence.sv').write_text('\n'.join(lines) + '\n', encoding='utf-8')


def cycle_for_step(step):
    op = step['op']
    if op == 'reset':
        return [(0,0,1,1,0,0,0,1200) for _ in range(step['cycles'])]
    if op == 'wait_ns' or op == 'wait_cycles':
        n = int(step['value']) if op == 'wait_cycles' else 1
        return [(1,1,1,1,0,0,0,1200) for _ in range(n)]
    if op == 'set_vdd_mv':
        return [(1,1,1,1,0,0,0,step['value'])]
    if op == 'write':
        return [(1,0,0,1,step['addr'],step['data'],0,1200)]
    if op == 'read_expect':
        return [(1,0,1,0,step['addr'],0,step['data'],1200)]
    if op == 'illegal_we_re_low':
        return [(1,0,0,0,step['addr'],0,0,1200)]
    raise ValueError(op)


def flatten_cycles():
    rows = []
    idx = 0
    for seq in SEQUENCES:
        for step in seq['steps']:
            for tup in cycle_for_step(step):
                reset_n, cs_n, we_n, re_n, addr, wdata, rdata, vdd = tup
                rows.append({
                    'cycle': idx,
                    'sequence': seq['name'],
                    'RESET_N': reset_n,
                    'CS_N': cs_n,
                    'WE_N': we_n,
                    'RE_N': re_n,
                    'ADDR': addr,
                    'WDATA': wdata,
                    'EXP_RDATA': rdata,
                    'VDD_MV': vdd,
                })
                idx += 1
    return rows


def write_vectors():
    rows = flatten_cycles()
    header = ['cycle','sequence','RESET_N','CS_N','WE_N','RE_N','ADDR','WDATA','EXP_RDATA','VDD_MV']
    lines = ['# FineSim-style synthetic vector', ' '.join(header)]
    for r in rows:
        lines.append(' '.join(str(r[h]) for h in header))
    (OUT / 'finesim_vector.vec').write_text('\n'.join(lines) + '\n', encoding='utf-8')

    v = []
    v.append('// Synthetic Verilog vector include')
    v.append('typedef struct packed {')
    v.append('  logic RESET_N, CS_N, WE_N, RE_N;')
    v.append('  logic [7:0] ADDR, WDATA, EXP_RDATA;')
    v.append('  logic [15:0] VDD_MV;')
    v.append('} mem_vec_t;')
    v.append(f'localparam int MEM_VEC_COUNT = {len(rows)};')
    v.append('mem_vec_t mem_vec [MEM_VEC_COUNT] = \'{')
    for i, r in enumerate(rows):
        comma = ',' if i < len(rows) - 1 else ''
        v.append("  '{" + f"{r['RESET_N']}, {r['CS_N']}, {r['WE_N']}, {r['RE_N']}, 8'h{r['ADDR']:02X}, 8'h{r['WDATA']:02X}, 8'h{r['EXP_RDATA']:02X}, 16'd{r['VDD_MV']}" + '}' + comma)
    v.append('};')
    (OUT / 'verilog_vector.v').write_text('\n'.join(v) + '\n', encoding='utf-8')


def write_report():
    text = '# Generation Report\n\n'
    text += 'Generated from a synthetic JEDEC-like excerpt. Not a compliance artifact.\n\n'
    text += '## Artifacts\n\n'
    for f in ['coverage_points.yaml', 'sequence_ir.json', 'generated_sequence.sv', 'finesim_vector.vec', 'verilog_vector.v']:
        text += f'- `{f}`\n'
    text += '\n## Human Review Items\n\n'
    text += '- Confirm read latency.\n- Confirm voltage acceptance criteria.\n- Confirm jitter model.\n- Review illegal command recovery semantics.\n'
    (OUT / 'generation_report.md').write_text(text, encoding='utf-8')


def main():
    write_coverage_yaml()
    write_sequence_ir()
    write_sv_sequence()
    write_vectors()
    write_report()
    print(f'Generated artifacts under {OUT}')

if __name__ == '__main__':
    main()
