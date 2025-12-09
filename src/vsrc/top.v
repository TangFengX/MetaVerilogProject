module top(
    input clk,
    input rst,
    input [4:0] btn,
    input [7:0] sw,
    output [7:0] seg0,
    output [7:0] seg1,
    output [7:0] seg2,
    output [7:0] seg3,
    output [7:0] seg4,
    output [7:0] seg5,
    output [7:0] seg6,
    output [7:0] seg7,
    output [15:0] ledr
);
    led my_led(
    .clk(clk),
    .rst(rst),
    .btn(btn),
    .sw(sw),
    .ledr(ledr)
);
seg my_seg(
    .clk(clk),
    .rst(rst),
    .o_seg0(seg0),
    .o_seg1(seg1),
    .o_seg2(seg2),
    .o_seg3(seg3),
    .o_seg4(seg4),
    .o_seg5(seg5),
    .o_seg6(seg6),
    .o_seg7(seg7)
);
endmodule


module led(
  input clk,
  input rst,
  input [4:0] btn,
  input [7:0] sw,
  output [15:0] ledr
);
  reg [31:0] count;
  reg [7:0] led;
  always @(posedge clk) begin
    if (rst) begin led <= 1; count <= 0; end
    else begin
      if (count == 0) led <= {led[6:0], led[7]};
      count <= (count >= 5000000 ? 32'b0 : count + 1);
    end
  end

  assign ledr = {led[7:5], led[4:0] ^ btn, sw};
endmodule


module seg(
  input clk,
  input rst,
  output [7:0] o_seg0,
  output [7:0] o_seg1,
  output [7:0] o_seg2,
  output [7:0] o_seg3,
  output [7:0] o_seg4,
  output [7:0] o_seg5,
  output [7:0] o_seg6,
  output [7:0] o_seg7
);

wire [7:0] segs [7:0];
assign segs[0] = 8'b11111101;
assign segs[1] = 8'b01100000;
assign segs[2] = 8'b11011010;
assign segs[3] = 8'b11110010;
assign segs[4] = 8'b01100110;
assign segs[5] = 8'b10110110;
assign segs[6] = 8'b10111110;
assign segs[7] = 8'b11100000;

parameter CLK_NUM = 5000000;

reg [31:0] count;
reg [2:0] offset;

always @(posedge clk) begin
  if(rst) begin count <= 0; offset <= 0; end
  else begin
    if(count == CLK_NUM) begin offset <= offset + 1; end
    count <= (count == CLK_NUM) ? 0 : count + 1;
  end
end

assign o_seg0 = ~segs[offset + 3'd0];
assign o_seg1 = ~segs[offset + 3'd1];
assign o_seg2 = ~segs[offset + 3'd2];
assign o_seg3 = ~segs[offset + 3'd3];
assign o_seg4 = ~segs[offset + 3'd4];
assign o_seg5 = ~segs[offset + 3'd5];
assign o_seg6 = ~segs[offset + 3'd6];
assign o_seg7 = ~segs[offset + 3'd7];

endmodule