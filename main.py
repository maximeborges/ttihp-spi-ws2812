# main.py - Automated Tiny Tapeout project generator
import os

import yaml
from amaranth.back import verilog

from src.project import Top

def get_module_name():
    """Read the top module name from info.yaml"""
    try:
        # Go up one directory to find info.yaml
        info_yaml_path = os.path.join(
            os.path.dirname(__file__), "info.yaml"
        )
        with open(info_yaml_path, "r") as f:
            info = yaml.safe_load(f)
        return info["project"]["top_module"]
    except Exception as e:
        print(f"Warning: Could not read module name from info.yaml: {e}")
        return "tt_um_set_reset_gate"  # fallback


def generate_tiny_tapeout_wrapper(amaranth_verilog, module_name=None):
    """Convert Amaranth-generated Verilog to Tiny Tapeout compatible format"""

    if module_name is None:
        module_name = get_module_name()

    # Simple wrapper template that instantiates the Amaranth core
    wrapper = f"""/*
 * Copyright (c) 2024 Mario Geiger
 * SPDX-License-Identifier: Apache-2.0
 * 
 * Auto-generated from Amaranth design - Set-Reset Gate
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
  
  // Instantiate the Amaranth-generated core module
  top core (
    .clk(clk),
    .rst(rst),
    
    .cs(ui_in[0]),
    .copi(ui_in[1]),
    
    .out(uo_out)
  );
  
  // All other output pins must be assigned to 0 when not used
  assign uio_out = 8'b0;
  assign uio_oe  = 8'b0;

  // List all unused inputs to prevent warnings
  wire _unused = &{{ena, ui_in[7:2], uio_in, 1'b0}};

endmodule

// Amaranth-generated core module
{amaranth_verilog}
"""

    return wrapper


if __name__ == "__main__":
    # Generate the Amaranth core module
    top = Top()
    amaranth_verilog = verilog.convert(top, ports=[top.cs, top.copi, top.out])

    # Generate the complete Tiny Tapeout wrapper (module name read from info.yaml)
    complete_project = generate_tiny_tapeout_wrapper(amaranth_verilog)

    # Write to verilog (same directory as this script)
    with open("src/project.v", "w") as f:
        f.write(complete_project)

    print(f"✅ Generated src/project.v from Amaranth Set-Reset Gate design! Module: {get_module_name()}")
