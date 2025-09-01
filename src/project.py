from amaranth import *
from amaranth.lib import wiring
from amaranth.lib.wiring import In, Out

from .spi import SPICommandInterface
from .ws2811 import WS2811

class Top(Elaboratable):
    """
    Top-level module containing the WS2812 driver and SPI interface.

    Parameters
    ----------

    Attributes
    ----------
    cs : Signal, in
        SPI chip select
    copi : Signal, in
        SPI data input
    out : Signal, out
        Up to 8x WS2812 outputs
    """

    def __init__(self):
        self.cs = Signal(1)
        self.copi = Signal(1)

        self.out = Signal(8)

        self.word_size = Signal(6)

        self.spi = SPICommandInterface()
        self.led_strips = [WS2811(), WS2811(), WS2811(), WS2811(), WS2811(), WS2811(), WS2811(), WS2811()]

        self.strip_count = Signal(4)
        self.strip_counter = Signal(4, init=0)

        super().__init__()

    def elaborate(self, platform):
        m = Module()

        m.submodules.spi = self.spi

        m.d.comb += [
            self.strip_count.eq(8),
            self.word_size.eq(24),
            self.spi.copi.eq(self.copi),
            self.spi.cs.eq(self.cs),

            self.spi.word_width.eq(self.word_size),
        ]
        for i in range(8):
            m.d.comb += [
                self.led_strips[i].enable.eq(0),
                self.led_strips[i].word_width.eq(self.word_size),
                self.out[i].eq(self.led_strips[i].data_out),
            ]
            m.submodules += self.led_strips[i]

        with m.Switch(self.strip_counter):
            for i in range(8):
                with m.Case(i):
                    m.d.comb += [
                        self.led_strips[i].enable.eq(self.spi.word_complete),
                        self.led_strips[i].data_in.eq(self.spi.word_received),
                    ]

        with m.If(self.spi.word_complete):
            with m.If(self.strip_counter < self.strip_count - 1):
                m.d.sync += [
                    self.strip_counter.eq(self.strip_counter + 1)
                ]
            with m.Else():
                m.d.sync += [
                    self.strip_counter.eq(0)
                ]

        return m
