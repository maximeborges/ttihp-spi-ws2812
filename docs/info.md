<!---

This file is used to generate your project datasheet. Please fill in the information below and delete any unused
sections.

You can also include images in this folder and reference them in the markdown. Each image must be less than
512 kb in size, and the combined size of all images must be less than 1 MB.
-->

## How it works

This project implements a classic "blinky" LED using a 24-bit counter that increments on every clock cycle. The design uses the most significant bit (MSB) of the counter as the LED output, which creates a visible blinking pattern. 

At a 50MHz clock frequency, the 24-bit counter takes 2^23 = 8,388,608 clock cycles to toggle the MSB, resulting in a blink rate of approximately 6Hz - perfect for visual confirmation that the chip is working. The LED output is connected to `uo_out[0]`, while all other outputs are tied to logic 0.

The design is automatically generated from Amaranth (Python HDL) code and wrapped for Tiny Tapeout compatibility, demonstrating a modern FPGA-to-ASIC design flow.

## How to test

To test this design:

1. **Power on** - The design will start blinking immediately when powered, no input signals required
2. **Observe LED** - Connect an LED (with appropriate current limiting resistor) to output pin `uo_out[0]` 
3. **Verify timing** - The LED should blink at approximately 6Hz (about 6 times per second)
4. **Check other outputs** - All other output pins (`uo_out[7:1]`, `uio_out`, `uio_oe`) should remain at logic 0

No external hardware is required beyond an LED and current limiting resistor. The design ignores all input pins and operates independently.

## External hardware

- **LED** - Any standard LED connected to `uo_out[0]`
- **Current limiting resistor** - Typically 220Ω to 1kΩ depending on LED and supply voltage
- **Optional oscilloscope** - To measure the exact blink frequency and verify timing
