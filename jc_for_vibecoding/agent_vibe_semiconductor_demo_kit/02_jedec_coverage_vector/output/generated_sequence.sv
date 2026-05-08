// Synthetic generated sequence skeleton
class generated_mem_sequence extends uvm_sequence;
  `uvm_object_utils(generated_mem_sequence)
  task body();
    // Sequence: reset_then_basic_write_read_bl4
    do_reset(2);
    wait_ns(5);
    mem_write(8'h10, 8'hA5, 4);
    wait_cycles(2);
    mem_read_expect(8'h10, 8'hA5); // latency needs review
    // Sequence: voltage_sweep_write_bl8
    set_vdd_mv(1080);
    mem_write(8'h20, 8'h5A, 8);
    set_vdd_mv(1200);
    mem_write(8'h21, 8'h5B, 8);
    set_vdd_mv(1320);
    mem_write(8'h22, 8'h5C, 8);
    // Sequence: illegal_command_no_corrupt
    mem_write(8'h30, 8'hC3, 4);
    drive_illegal_we_re_low(8'h30);
    wait_cycles(2);
    mem_read_expect(8'h30, 8'hC3); // latency needs review
  endtask
endclass
