/*
 * Copyright (c) 2024 Mario Geiger
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_blinky (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

  // 24-bit counter for blinky LED
  reg [23:0] counter;
  
  always @(posedge clk) begin
    if (!rst_n) begin
      counter <= 24'h0;
    end else begin
      counter <= counter + 1;
    end
  end

  // Connect LED to MSB of counter (uo_out[0])
  assign uo_out[0] = counter[23];
  
  // All other output pins must be assigned to 0 when not used
  assign uo_out[7:1] = 7'b0;
  assign uio_out = 8'b0;
  assign uio_oe  = 8'b0;

  // List all unused inputs to prevent warnings
  wire _unused = &{ena, ui_in, uio_in, 1'b0};

endmodule
