#include "tester_b.hpp"

void basic_function_check(BSession& b) {

    b.loadPattern("pattern_b_generated.pat");
    b.power.setRail("VDD", 1.20); // NEEDS REVIEW: confirm platform B voltage semantics
    b.timing.setPeriod("CLK", 5.0);
    b.pin.force("RESET_N", 0);
    b.wait.ns(10 * 1000);
    b.pin.force("RESET_N", 1);

    BRunResult result = b.executePattern("BASIC_READ");
    b.datalog.scalar("basic_read_pass", result.passed);

    // This function has no direct platform B mapping in this demo.
    // TODO HUMAN REVIEW: unsupported source call: a_enable_binning("engineering_debug");
}
