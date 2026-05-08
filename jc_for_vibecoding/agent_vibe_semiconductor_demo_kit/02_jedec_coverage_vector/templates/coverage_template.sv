package coverage_template_pkg;
  // Agent should fill coverage points derived from requirements.
  covergroup mem_cg @(posedge vif.CLK);
    option.per_instance = 1;
    cp_cmd: coverpoint {vif.CS_N, vif.WE_N, vif.RE_N};
    cp_vdd: coverpoint vif.VDD_MV;
    cp_addr: coverpoint vif.ADDR;
  endgroup
endpackage
