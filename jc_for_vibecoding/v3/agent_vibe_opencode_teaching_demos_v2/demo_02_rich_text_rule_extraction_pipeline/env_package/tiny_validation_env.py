class TinyValidationEnv:
    def __init__(self):
        self.signals = {"rst_n": 1, "ready": 0, "pass_flag": 1, "error_count": 0}
        self.params = {"supply_vdd": 1.0, "clock_jitter_ps": 0}

    def set_signal(self, name, value):
        self.signals[name] = value
        if name == "rst_n" and value == 1:
            self.signals["ready"] = 1

    def set_param(self, name, value):
        self.params[name] = value

    def wait_ns(self, ns):
        return None

    def basic_transaction(self):
        self.signals["pass_flag"] = 1
        return True

    def check_equal(self, name, expected):
        current = self.signals.get(name, self.params.get(name))
        assert current == expected, f"{name} expected {expected}, got {current}"
