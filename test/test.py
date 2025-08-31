# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


@cocotb.test()
async def test_set_reset_gate(dut):
    dut._log.info("Start Set-Reset Gate Test")

    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    # Initial setup
    dut._log.info("Initial Setup")
    dut.ena.value = 1
    dut.ui_in.value = 0  # set=0, reset=0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)

    # Helper function to set inputs and wait for result
    async def set_inputs(set_val, reset_val):
        # ui_in[0] = SET, ui_in[1] = RESET
        dut.ui_in.value = (reset_val << 1) | set_val
        await ClockCycles(dut.clk, 2)
        output = dut.uo_out.value & 1  # Get bit 0
        dut._log.info(f"SET={set_val}, RESET={reset_val} -> OUTPUT={output}")
        return output

    # Test 1: Initial state (both inputs 0, should maintain state)
    dut._log.info("Test 1: Initial state")
    output = await set_inputs(0, 0)
    initial_state = output

    # Test 2: Set operation (set=1, reset=0 -> output=1)
    dut._log.info("Test 2: SET operation")
    output = await set_inputs(1, 0)
    assert output == 1, f"Expected output=1 when SET=1, RESET=0, got {output}"

    # Test 3: Hold state (set=0, reset=0 -> maintain output=1)
    dut._log.info("Test 3: Hold state after SET")
    output = await set_inputs(0, 0)
    assert output == 1, f"Expected output=1 when holding after SET, got {output}"

    # Test 4: Reset operation (set=0, reset=1 -> output=0)
    dut._log.info("Test 4: RESET operation")
    output = await set_inputs(0, 1)
    assert output == 0, f"Expected output=0 when SET=0, RESET=1, got {output}"

    # Test 5: Hold state (set=0, reset=0 -> maintain output=0)
    dut._log.info("Test 5: Hold state after RESET")
    output = await set_inputs(0, 0)
    assert output == 0, f"Expected output=0 when holding after RESET, got {output}"

    # Test 6: Priority test (set=1, reset=1 -> reset wins, output=0)
    dut._log.info("Test 6: Priority test (RESET wins)")
    output = await set_inputs(1, 1)
    assert output == 0, (
        f"Expected output=0 when both SET=1 and RESET=1 (reset priority), got {output}"
    )

    # Test 7: Set again after priority test
    dut._log.info("Test 7: SET after priority test")
    output = await set_inputs(1, 0)
    assert output == 1, (
        f"Expected output=1 when SET=1, RESET=0 after priority test, got {output}"
    )

    # Test 8: Verify unused outputs are 0
    dut._log.info("Test 8: Verify unused outputs")
    output_val = dut.uo_out.value
    other_bits = (output_val >> 1) & 0x7F
    assert other_bits == 0, f"Expected other output bits to be 0, got {other_bits}"

    # Verify that bidirectional outputs are 0
    assert dut.uio_out.value == 0, f"Expected uio_out to be 0, got {dut.uio_out.value}"
    assert dut.uio_oe.value == 0, f"Expected uio_oe to be 0, got {dut.uio_oe.value}"

    dut._log.info("✅ All Set-Reset Gate tests passed!")
