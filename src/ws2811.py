# Copyright (C) 2021 Hans Baier hansfbaier@gmail.com
# Modified by Maxime Borges
#
# SPDX-License-Identifier: Apache-2.0
#
from math import log2, ceil

from amaranth import *
from amaranth.build import Platform

from .shared import MAX_WORD_WIDTH

# Split the send of each bit of data into 3 cycles
# First is always high, second is high for a 1 and low for a 0, third is always low
CYCLE_LEN_HIGH = 2
CYCLE_LEN_LOW = 1
CYCLE_LEN = CYCLE_LEN_HIGH + CYCLE_LEN_LOW


class WS2811(Elaboratable):
    def __init__(self):
        # I / O
        self.clk = Signal()

        self.word_size = Signal()

        self.enable = Signal()
        self.data_in = Signal(MAX_WORD_WIDTH)
        self.data_out = Signal()

    def elaborate(self, platform: Platform) -> Module:
        m = Module()

        data_in = Signal.like(self.data_in)

        current_bit = Signal()

        bit_counter = Signal(ceil(log2(MAX_WORD_WIDTH)))
        cycle_counter = Signal(2)

        m.d.comb += [
            current_bit.eq(data_in.bit_select(bit_counter, 1)),
        ]

        with m.FSM():
            with m.State("IDLE"):
                m.d.comb += [
                    self.data_out.eq(0),
                ]
                
                with m.If(self.enable):
                    m.d.sync += [data_in.eq(self.data_in)]
                    m.next = "STREAMING"
            
            with m.State("STREAMING"):
                m.d.sync += [
                    cycle_counter.eq(cycle_counter + 1),
                ]

                with m.If(~self.enable):
                    m.next = "IDLE"

                with m.If(cycle_counter < Mux(current_bit, CYCLE_LEN_HIGH, CYCLE_LEN_LOW)):
                    m.d.comb += self.data_out.eq(1)
                with m.Else():
                    m.d.comb += self.data_out.eq(0)

                with m.If(cycle_counter >= CYCLE_LEN):
                    m.d.sync += [
                        cycle_counter.eq(0),
                        bit_counter.eq(bit_counter + 1),
                    ]

                    with m.If(bit_counter >= self.word_size):
                        m.next = "IDLE"

        return m


if __name__ == "__main__":
    from amaranth.back import verilog

    ws2811 = WS2811()

    with open("src/ws2811.v", "w") as f:
        f.write(verilog.convert(ws2811))
