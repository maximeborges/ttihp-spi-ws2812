# Sample testbench for a Tiny Tapeout project

This is a sample testbench for a Tiny Tapeout project. It uses [cocotb](https://docs.cocotb.org/en/stable/) to drive the DUT and check the outputs.
See below to get started or for more information, check the [website](https://tinytapeout.com/hdl/testing/).

## Prerequisites

⚠️ **First time setup?** See [../SETUP.md](../SETUP.md) for complete dependency installation guide.

**Quick setup:**
```bash
# Install system dependencies (macOS):
brew install icarus-verilog

# Install Python dependencies:
pip install -r ../requirements.txt
```

## Setting up

1. Edit [Makefile](Makefile) and modify `PROJECT_SOURCES` to point to your Verilog files.
2. Edit [tb.v](tb.v) and replace `tt_um_example` with your module name.

## How to run

**Option A: Use the wrapper script (recommended):**
```sh
./run_tests.sh
```

**Option B: Manual make (may need environment setup):**
```sh
make -B
```

To run gatelevel simulation, first harden your project and copy `../runs/wokwi/results/final/verilog/gl/{your_module_name}.v` to `gate_level_netlist.v`.

Then run:

```sh
make -B GATES=yes
```

## How to view the VCD file

Using GTKWave
```sh
gtkwave tb.vcd tb.gtkw
```

Using Surfer
```sh
surfer tb.vcd
```
