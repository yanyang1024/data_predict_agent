#include "tester_b.hpp"

void reference_smoke_test(BSession& b) {
    b.loadPattern("reference_pattern_b.pat");
    b.power.setRail("VDD", 1.20);
    b.timing.setPeriod("CLK", 5.0);
    b.pin.force("RESET_N", 0);
    b.wait.ns(10000);
    b.pin.force("RESET_N", 1);

    BRunResult result = b.executePattern("REFERENCE_READ");
    b.datalog.scalar("reference_read_pass", result.passed);
}
