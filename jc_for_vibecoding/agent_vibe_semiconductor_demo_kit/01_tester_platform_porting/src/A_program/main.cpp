#include "tester_a.hpp"

void basic_function_check() {
    a_load_pattern("pattern_a.pat");
    a_set_voltage("VDD", 1.20);
    a_set_timing("CLK", 5.0);
    a_force_pin("RESET_N", 0);
    a_wait_us(10);
    a_force_pin("RESET_N", 1);

    AResult result = a_run_pattern("BASIC_READ");
    a_log_value("basic_read_pass", result.pass_count);

    // This function has no direct platform B mapping in this demo.
    a_enable_binning("engineering_debug");
}
