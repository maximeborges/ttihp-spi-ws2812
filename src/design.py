# design.py - Automated Tiny Tapeout project generator
from amaranth import Elaboratable, Module, Signal
from amaranth.back import verilog


class Blinky(Elaboratable):
    def __init__(self):
        self.led = Signal()  # output pin

    def elaborate(self, platform):
        m = Module()
        cnt = Signal(24)  # 24-bit free-running counter
        m.d.sync += cnt.eq(cnt + 1)  # increments each clock
        m.d.comb += self.led.eq(cnt[-1])  # toggle LED with MSB
        return m


def generate_tiny_tapeout_wrapper(amaranth_verilog, module_name="tt_um_blinky"):
    """Convert Amaranth-generated Verilog to Tiny Tapeout compatible format"""

    # Simple wrapper template that instantiates the Amaranth core
    wrapper = f"""/*
 * Copyright (c) 2024 Mario Geiger
 * SPDX-License-Identifier: Apache-2.0
 * 
 * Auto-generated from Amaranth design
 */

`default_nettype none

module {module_name} (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

  // Internal signals for the Amaranth-generated core
  wire rst = !rst_n;  // Convert active-low reset to active-high
  wire core_led;
  
  // Instantiate the Amaranth-generated core module
  top core (
    .clk(clk),
    .rst(rst),
    .led(core_led)
  );
  
  // Connect core LED output to Tiny Tapeout output
  assign uo_out[0] = core_led;
  
  // All other output pins must be assigned to 0 when not used
  assign uo_out[7:1] = 7'b0;
  assign uio_out = 8'b0;
  assign uio_oe  = 8'b0;

  // List all unused inputs to prevent warnings
  wire _unused = &{{ena, ui_in, uio_in, 1'b0}};

endmodule

// Amaranth-generated core module
{amaranth_verilog}
"""

    return wrapper


if __name__ == "__main__":
    # Generate the Amaranth core module
    top = Blinky()
    amaranth_verilog = verilog.convert(top, ports=[top.led])

    # Generate the complete Tiny Tapeout wrapper
    complete_project = generate_tiny_tapeout_wrapper(amaranth_verilog)

    # Write to project.v (same directory as this script)
    with open("project.v", "w") as f:
        f.write(complete_project)

    print("✅ Generated project.v from Amaranth design!")
