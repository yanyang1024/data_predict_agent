from __future__ import annotations


def begin_sequence(log, name):
    log.append({'event': 'begin_sequence', 'name': name})


def end_sequence(log, name):
    log.append({'event': 'end_sequence', 'name': name})


def drive(log, signal, value, duration=None):
    log.append({'op': 'drive', 'signal': signal, 'value': value, 'duration': duration})


def expect(log, signal, relation, value, within_cycles=None):
    log.append({'op': 'expect', 'signal': signal, 'relation': relation, 'value': value, 'within_cycles': within_cycles})


def wait_time(log, duration):
    log.append({'op': 'wait_time', 'duration': duration})


def wait_cycles(log, cycles):
    log.append({'op': 'wait_cycles', 'cycles': cycles})


def write_bus(log, addr_signal, data_signal, address_expr, data_expr):
    log.append({'op': 'write_bus', 'addr_signal': addr_signal, 'data_signal': data_signal, 'address': address_expr, 'data': data_expr})


def set_jitter(log, clock_signal, jitter_ns):
    log.append({'op': 'set_jitter', 'clock_signal': clock_signal, 'jitter_ns': jitter_ns})
