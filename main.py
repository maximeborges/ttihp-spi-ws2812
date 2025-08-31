from amaranth.back import verilog
from src.top import Top

top = Top()

with open("src/top.v", "w") as f:
    f.write(verilog.convert(top))
