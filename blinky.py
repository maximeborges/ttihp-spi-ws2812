# blinky.py
from amaranth import Elaboratable, Module, Signal
from amaranth.back import verilog


class Blinky(Elaboratable):
    def __init__(self):
        self.led = Signal()  # output pin

    def elaborate(self, platform):
        m = Module()
        cnt = Signal(24)  # 24-bit free-running counter
        m.d.sync += cnt.eq(cnt + 1)  # increments each clock
        m.d.comb += self.led.eq(cnt[-1])  # toggle LED with MSB
        return m


if __name__ == "__main__":
    top = Blinky()
    # NOTE: Amaranth will add sync clock/reset ports automatically.
    # We'll keep the default Verilog module name "top" to stay simple.
    with open("src/amaranth_generated.v", "w") as f:
        f.write(verilog.convert(top, ports=[top.led]))
