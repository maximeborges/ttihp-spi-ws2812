#
# Copyright (c) 2020 Great Scott Gadgets <info@greatscottgadgets.com>
# Modified by Maxime Borges
#
# SPDX-License-Identifier: BSD-3-Clause

"""SPI and derived interfaces."""

from amaranth import Signal, Module, Cat, Elaboratable, ClockDomain
from amaranth.build import Platform

from .shared import MAX_WORD_WIDTH


class SPICommandInterface(Elaboratable):
    """Variant of an SPIDeviceInterface that accepts command-prefixed data.

    I/O signals:
        I: sck           -- SPI clock, from the SPI master
        I: sdi           -- SPI data in
        I: cs            -- chip select, active high (as we assume your I/O will use PinsN)

        I: word_size     -- the size of the word to receive in bits.


        O: command       -- the command read from the SPI bus
        O: command_ready -- a new command is ready

        O: word_received -- the most recent word received
        O: word_complete -- strobe indicating a new word is present on word_in

        O: idle          -- true iff the register interface is currently doing nothing
        O: stalled       -- true iff the register interface cannot accept data until this transaction ends
    """

    def __init__(self):
        self.command_size = 8
        self.max_word_width = MAX_WORD_WIDTH

        #
        # I/O port.
        #

        # SPI
        self.copi = Signal()
        self.cs = Signal()
        self.clk = Signal()

        self.word_width = Signal(6)

        # Command I/O.
        self.command = Signal(self.command_size)
        self.command_ready = Signal()

        # Data I/O
        self.word_received = Signal(self.max_word_width)
        self.word_complete = Signal()

        # Status
        self.idle = Signal()
        self.stalled = Signal()

    def connect_to_resource(self, spi_resource):
        return [
            spi_resource.copi.eq(self.spi_bus_out.sdo),
            spi_resource.clk.eq(self.spi_bus_out.sck),
            spi_resource.cs.eq(self.spi_bus_out.cs),
        ]

    def elaborate(self, platform: Platform) -> Module:
        m = Module()

        m.domains.sync = ClockDomain(clk_edge="neg")

        # Bit counter: counts the number of bits received.
        bit_count = Signal(range(0, self.max_word_width + 1))

        # Shift registers for our command and data.
        current_command = Signal.like(self.command)
        current_word = Signal.like(self.word_received)

        # De-assert our control signals unless explicitly asserted.
        m.d.sync += [self.command_ready.eq(0), self.word_complete.eq(0)]

        with m.FSM() as fsm:
            m.d.comb += [
                self.idle.eq(fsm.ongoing("IDLE")),
                self.stalled.eq(fsm.ongoing("STALL")),
            ]

            # STALL: entered when we can't accept new bits -- either when
            # CS starts asserted, or when we've received more data than expected.
            with m.State("STALL"):
                # Wait for CS to clear.
                with m.If(~self.cs):
                    m.next = "IDLE"

            # We ignore all data until chip select is asserted, as that data Isn't For Us (TM).
            # We'll spin and do nothing until the bus-master addresses us.
            with m.State("IDLE"):
                m.d.sync += [bit_count.eq(0)]

                with m.If(self.cs):
                    m.next = "RECEIVE_COMMAND"

            # Once CS is low, we'll shift in our command.
            with m.State("RECEIVE_COMMAND"):
                # If CS is de-asserted early; our transaction is being aborted.
                with m.If(~self.cs):
                    m.next = "IDLE"

                # Continue shifting in data until we have a full command.
                with m.If(bit_count < self.command_size):
                    m.d.sync += [
                        bit_count.eq(bit_count + 1),
                        current_command.eq(Cat(self.copi, current_command[:-1])),
                    ]

                # ... and then pass that command out to our controller.
                with m.Else():
                    m.d.sync += [
                        bit_count.eq(0),
                        self.command_ready.eq(1),
                        self.command.eq(current_command),
                    ]
                    m.next = "PROCESSING"

            # Give our controller a wait state to prepare any response they might want to...
            with m.State("PROCESSING"):
                m.next = "SHIFT_DATA"

            # Finally, exchange data.
            with m.State("SHIFT_DATA"):
                # If CS is de-asserted early; our transaction is being aborted.
                with m.If(~self.cs):
                    m.next = "IDLE"

                # m.d.sync += self.sdo.eq(current_word[-1])

                # Continue shifting data until we have a full word.
                with m.If(bit_count < self.word_width):
                    m.d.sync += [
                        bit_count.eq(bit_count + 1),
                        current_word.eq(Cat(self.copi, current_word[:-1])),
                    ]

                # ... and then output that word on our bus.
                with m.Else():
                    m.d.sync += [
                        bit_count.eq(0),
                        self.word_complete.eq(1),
                        self.word_received.eq(current_word),
                    ]

                    # Stay in the stall state until CS is de-asserted.
                    m.next = "STALL"

        return m
