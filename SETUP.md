# Setup Guide for Tiny Tapeout Testing

This document explains the dependencies needed to run tests from scratch.

## Why `make` doesn't work immediately

The testing setup requires several external dependencies that aren't automatically installed:

### 1. **Icarus Verilog Simulator**
```bash
# Error without it:
# "Unable to locate command >iverilog<"

# Install on macOS:
brew install icarus-verilog

# Install on Ubuntu/Linux (used in CI):
sudo apt-get update && sudo apt-get install -y iverilog
```

### 2. **Python Dependencies**
```bash
# Install all required Python packages:
pip install -r requirements.txt

# This includes:
# - amaranth (HDL design)
# - amaranth-yosys (synthesis)
# - PyYAML (configuration parsing)
# - cocotb (Python testbench framework)
# - pytest (testing framework)
```

### 3. **Python Environment Issues**
Cocotb sometimes has trouble finding Python modules, especially in virtual environments.

**Error seen:**
```
ModuleNotFoundError: No module named 'pygpi'
```

**Solutions:**
- **Option A:** Use explicit PYTHONPATH:
```bash
PYTHONPATH=$PYTHONPATH:$(python -c "import site; print(site.getsitepackages()[0])") make -B
```

- **Option B:** Create a wrapper script (recommended)

## Complete Setup from Scratch

### 1. Install System Dependencies
```bash
# macOS:
brew install icarus-verilog

# Ubuntu/Linux:
sudo apt-get update && sudo apt-get install -y iverilog
```

### 2. Install Python Dependencies
```bash
# From project root:
uv sync
```

### 3. Generate Verilog
```bash
uv run python main.py
```

### 4. Run Tests
```bash
cd test

# Option A: With explicit path
PYTHONPATH=$PYTHONPATH:$(python -c "import site; print(site.getsitepackages()[0])") make -B

# Option B: Use our wrapper script
./run_tests.sh
```

## Why This Happens

1. **Icarus Verilog** isn't included in most default installations
2. **Cocotb** is a specialized tool that bridges Python and Verilog simulators
3. **Python path detection** can fail in certain virtual environments
4. **GitHub Actions** handle this automatically with our setup, but local development needs manual setup

## CI/CD vs Local Development

**GitHub Actions** (works automatically):
- Uses `requirements.txt` to install everything
- Ubuntu environment has predictable Python paths
- Controlled environment

**Local Development** (needs setup):
- Different operating systems (macOS, Linux, Windows)
- Various Python installations (system, pyenv, conda, etc.)
- Different virtual environment configurations

This is why the CI passes but local `make` fails from scratch.
