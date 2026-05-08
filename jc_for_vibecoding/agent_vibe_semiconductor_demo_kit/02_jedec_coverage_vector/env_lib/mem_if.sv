interface mem_if(input logic CLK);
  logic RESET_N;
  logic CS_N;
  logic WE_N;
  logic RE_N;
  logic [7:0] ADDR;
  logic [7:0] WDATA;
  logic [7:0] RDATA;
  logic [15:0] VDD_MV;
endinterface
