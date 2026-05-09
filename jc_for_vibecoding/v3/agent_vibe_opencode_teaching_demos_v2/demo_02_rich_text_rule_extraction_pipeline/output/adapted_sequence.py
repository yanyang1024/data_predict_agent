# Auto-generated teaching sequence. Syntax-validated only; logic requires human review.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from env_package.tiny_validation_env import TinyValidationEnv

def run(env=None):
    env = env or TinyValidationEnv()
    # Rule: RESET_STABILITY - Verify reset release stability
    env.set_signal('rst_n', 0)
    env.wait_ns(10)
    env.set_signal('rst_n', 1)
    env.wait_ns(20)
    env.check_equal('ready', 1)
    # Rule: VOLTAGE_SWEEP - Validate operation across voltage range
    env.set_param('supply_vdd', 0.9)
    env.basic_transaction()
    env.check_equal('pass_flag', 1)
    env.set_param('supply_vdd', 1.0)
    env.basic_transaction()
    env.check_equal('pass_flag', 1)
    env.set_param('supply_vdd', 1.1)
    env.basic_transaction()
    env.check_equal('pass_flag', 1)
    # Rule: JITTER_TOLERANCE - Validate clock jitter tolerance
    env.set_param('clock_jitter_ps', 50)
    env.basic_transaction()
    env.check_equal('error_count', 0)
    return env

if __name__ == '__main__':
    run()
    print('sequence syntax and dry run passed')
