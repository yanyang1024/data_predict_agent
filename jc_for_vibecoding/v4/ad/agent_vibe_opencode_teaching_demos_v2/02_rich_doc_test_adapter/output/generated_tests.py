# Auto-generated teaching demo tests. Human review required for verification semantics.
class DemoEnvProtocol:
    pass

def test_RESET_STABILITY(env):
    """复位后 ready 信号应在 3 个周期内拉高 Expected: ready == 1"""
    env.reset(cycles=1)
    env.wait_cycles(3)
    env.expect_signal('ready', 1)

def test_WRITE_READ_BACK(env):
    """写寄存器后可以读回相同值 Expected: read_data == 0xA5"""
    env.write_reg(0x10, 0xA5)
    actual = env.read_reg(0x10)
    env.assert_equal(actual, 0xA5)

def test_JITTER_TOLERANCE(env):
    """注入时钟抖动后状态机不应进入 error Expected: error == 0"""
    env.clock_jitter(50)
    env.wait_cycles(5)
    env.expect_signal('error', 0)
