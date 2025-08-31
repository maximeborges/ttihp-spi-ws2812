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
        Up to 16x WS2812 outputs
    """

    # clk: In(1)
    # rst: In(1)
    # cs: In(1)
    # copi: In(1)
    # out0: Out(1)

    def __init__(self):
        self.clk = Signal(1)
        self.rst = Signal(1)

        self.cs = Signal(1)
        self.copi = Signal(1)

        self.out0 = Signal(1)

        self.word_size = Signal(6)

        self.spi = SPICommandInterface()
        self.led0 = WS2811()

        super().__init__()

    def elaborate(self, platform):
        m = Module()

        m.d.comb += [
            self.spi.copi.eq(self.copi),
            self.spi.cs.eq(self.cs),
            self.spi.clk.eq(self.clk),
            self.led0.clk.eq(self.clk),
            
            self.out0.eq(self.led0.data_out),

            self.led0.word_size.eq(self.word_size),
            self.spi.word_width.eq(self.word_size),
            self.led0.enable.eq(self.spi.word_complete),
            self.led0.data_in.eq(self.spi.word_received),
        ]

        m.submodules.led1 = self.led0
        m.submodules.spi = self.spi

        return m
