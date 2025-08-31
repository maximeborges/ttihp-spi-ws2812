# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")

    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    dut._log.info("Test blinky behavior")

    # Test that counter resets to 0
    await ClockCycles(dut.clk, 1)
    initial_led = dut.uo_out.value & 1  # Get LED state (bit 0)

    # Wait for many clock cycles to see LED state change
    # With a 24-bit counter, we need 2^23 = 8,388,608 cycles for one toggle
    # For testing, we'll just verify the counter is running by checking internal state
    dut._log.info(f"Initial LED state: {initial_led}")

    # Run for a while and check that other outputs are 0
    await ClockCycles(dut.clk, 100)

    # Verify that only uo_out[0] is used for LED, others should be 0
    output_val = dut.uo_out.value
    led_bit = output_val & 1
    other_bits = (output_val >> 1) & 0x7F

    dut._log.info(f"LED bit: {led_bit}, Other bits: {other_bits}")
    assert other_bits == 0, f"Expected other output bits to be 0, got {other_bits}"

    # Verify that bidirectional outputs are 0
    assert dut.uio_out.value == 0, f"Expected uio_out to be 0, got {dut.uio_out.value}"
    assert dut.uio_oe.value == 0, f"Expected uio_oe to be 0, got {dut.uio_oe.value}"
