{
  "env_name": "teaching_verification_env",
  "python_api": {
    "reset": "env.reset(cycles=1)",
    "wait_cycles": "env.wait_cycles(cycles)",
    "expect_ready": "env.expect_signal('ready', 1)",
    "write_reg": "env.write_reg(addr, data)",
    "read_reg": "env.read_reg(addr)",
    "assert_equal": "env.assert_equal(actual, expected)",
    "inject_clock_jitter": "env.clock_jitter(ppm)",
    "assert_no_error": "env.expect_signal('error', 0)"
  },
  "unsupported": [],
  "human_review_required": [
    "ready 信号时序是否应严格等于 3 周期内",
    "寄存器地址和数据是否覆盖足够场景",
    "clock jitter ppm 阈值是否来自正式规格"
  ]
}