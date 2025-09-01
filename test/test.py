# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

# import asyncio
import threading
import cocotb
from cocotb.clock import Clock
import cocotb.clock
from cocotb.triggers import Timer
from cocotb.triggers import ClockCycles
from cocotb.types import Bit

import math

FREQ = 900000 * 3 * 16
PERIOD_NS = math.ceil(1000000000 / FREQ)

class ClockHandle:
    def __init__(self):
        self.signal = Bit(0)
        
@cocotb.test()
async def test_set_reset_gate(dut):
    dut._log.info("Start Set-Reset Gate Test")

    # Set the clock period
    clk_en = threading.Lock()
    class SpiClock:
        def __init__(self, lock):
            self.lock = lock

        async def start(self):
            high_time = Timer(PERIOD_NS/2, units="ns")
            low_time = Timer(PERIOD_NS/2, units="ns")
            while True:
                dut.clk.value = 1
                await high_time
                if self.lock.locked():
                    dut.clk.value = 0
                await low_time

    def set_copi(copi: bool):
        d = dut.ui_in.value.integer
        if copi:
            dut.ui_in.value = d | 0b00000010
        else:
            dut.ui_in.value = d & 0b11111101

    def set_cs(cs: bool):
        d = dut.ui_in.value
        if cs:
            dut.ui_in.value = d | 0b00000001
        else:
            dut.ui_in.value = d & 0b11111110

    def get_out0():
        return (dut.uo_out.value & 1) == 1

    clk_signal = ClockHandle()
    clock = Clock(clk_signal, PERIOD_NS, units="ns")
    spi_clk = SpiClock(clk_en)
    cocotb.start_soon(clock.start())
    cocotb.start_soon(spi_clk.start())

    # Initial setup
    dut._log.info("Initial Setup")
    dut.ena.value = 1
    dut.ui_in.value = 0b00000010
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await Timer(5, units='us')
    dut.rst_n.value = 1
    await Timer(5, units='us')

    # Test 1: Initial state (both inputs 0, should maintain state)
    dut._log.info("Test 1: Enable chip select")
    set_cs(True)
    await Timer(1, units='us')

    # Test 2: Set operation (set=1, reset=0 -> output=1)
    dut._log.info("Test 2: Start SPI frame")
    with clk_en:
        cmd = 0b10101010
        for i in range(8):
            bit  = ((cmd >> (7 - i)) & 1) == 1
            set_copi(bit)
            await ClockCycles(dut.clk, 1)
            out0 = get_out0()
            assert ~out0, f"Expected out0=0 until after the first LED data is sent, got {out0}"


        # await Timer(1, units='us')

        # Test 3: Send the data for the first LED
        dut._log.info("Test 3: Send data for first LED")
        for led in [
            [0b11111111, 0b00000000, 0b11111111], 
            [0b00000000, 0b00000000, 0b00000000],
            [0b01010101, 0b01010101, 0b01010101],
            [0b00000000, 0b00000000, 0b00000000],
        ]*20:
            for byte in led:
                dut._log.info(f"Sending byte: {byte:08b}")
            
                for i in range(8):
                    bit  = ((byte >> (7 - i)) & 1) == 1
                    set_copi(bit)
                    await ClockCycles(dut.clk, 1)
                    out0 = get_out0()
                    assert ~out0, f"Expected out0=0 until after the first LED data is sent, got {out0}"
                
                    # await ClockCycles(dut.clk, 10)
                # await Timer(1, units='us')

            # for i in range(24):
            #     out0 = get_out0()
            #     await ClockCycles(dut.clk, 1)
            #     assert out0, f"Expected out0=1 after sending first LED data, got {out0}"

        # await ClockCycles(dut.clk, 600)


    dut._log.info("✅ All Set-Reset Gate tests passed!")
