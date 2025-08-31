#!/bin/bash

# Simple wrapper script to run cocotb tests with proper Python environment

echo "🔧 Checking dependencies..."

# Check if iverilog is available
if ! command -v iverilog &> /dev/null; then
    echo "❌ iverilog not found. Install with:"
    echo "   macOS: brew install icarus-verilog"
    echo "   Linux: sudo apt-get install iverilog"
    exit 1
fi

# Check if cocotb is available
if ! python -c "import cocotb" &> /dev/null; then
    echo "❌ cocotb not found. Install with:"
    echo "   pip install -r ../requirements.txt"
    exit 1
fi

echo "✅ Dependencies found"

# Set Python path to help cocotb find modules
export PYTHONPATH="$PYTHONPATH:$(python -c "import site; print(':'.join(site.getsitepackages()))")"

echo "🧪 Running tests..."

# Clean and run tests
make clean
make -B

if [ $? -eq 0 ]; then
    echo "✅ Tests completed successfully!"
    echo "📊 View waveforms with: gtkwave tb.vcd tb.gtkw"
else
    echo "❌ Tests failed"
    exit 1
fi
