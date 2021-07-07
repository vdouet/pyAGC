"""Copyright (C) 2021  Victor Douet <victor.douet@gmail.com>

This file is part of pyAGC.
pyAGC is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

pyAGC is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with pyAGC.  If not, see <https://www.gnu.org/licenses/>.
"""

import os
import numpy as np

from timer import _Timer
from memory import _Memory
from registers import _Registers
from interrupts import _Interrupts
from io_channels import _IO_channels


class Cpu:
    def __init__(self) -> None:

        self.timer = _Timer()
        self.reg = _Registers()
        self.mem = _Memory()
        self.irq = _Interrupts(self.mem, self.reg)

        # Slicing a numpy array creates a view on the original array. This is
        # done because channel 1 and 2 overlap with register L and Q
        self.io = _IO_channels(
            self.mem.unswitched[self.reg.L:self.reg.L+1],
            self.mem.unswitched[self.reg.Q:self.reg.Q+1])

        self.extracode_flag = False
        self.check_parity_flag = False

        # Why 32? I guess for 32 bits but why.
        # TODO: Investigate why / 32.
        self.parities = np.zeros((int(self.mem.common_fixed_banks *
                                      (self.mem.fixed_words / 32))),
                                 dtype=np.uint32)

    def run(self) -> None:

        while True:

            # Execute a CPU cycle every 11.72 µs or more depending on the
            # number of MCT taken by instructions
            # FIXME: Need to check what is the correct way to handle an
            # instruction taking 1 MCT (or more) inside a CPU cycle.
            if self.timer.do_cycle():

                # print("Loop time: " + str(self.timer.elapsed_time_ns * 1e-3))
                # print("Total time: " + str(self.timer.total_cycle_time * 1e-3))

                self.timer.wait_cycle(1)
                # print("Wait time: " + str(self.timer.elapsed_wait * 1e-3))

                self.timer.added_cycle = 1
                self._execute_cycle()

    def _execute_cycle(self) -> None:
        pass

    def load_core_rope(self, bin_path: str) -> None:
        """Method to load provided .bin file into AGC's memory.

        Mostly taken from agc_engine_init.c from yaAGC as I haven't explored
        how yaYUL function yet.

        Args:
            bin_path (str): Path to the .bin file to load.

        Raises:
            TypeError: if bin_path is null or not a str.
            FileNotFoundError: if bin_path does not point to an existing file.
            ValueError: if .bin file size is not even.
            ValueError: if .bin file size to big for AGC's memory.
        """

        # Check if the provided path is a string and not empty.
        if not isinstance(bin_path, str) or not bin_path:
            raise TypeError("Provided path is either empty or not a string.")

        # If the provided file does not end with the .bin extension, add it.
        if not bin_path.lower().endswith(".bin"):
            bin_path = bin_path + ".bin"

        # Check if file exist.
        if not os.path.isfile(bin_path):
            raise FileNotFoundError(f"Error: file does not exist '{bin_path}'")

        # File size should be an even number of bytes.
        if os.path.getsize(bin_path) % 2:
            raise ValueError("Incorrect file size (size is not even).")

        # File size should fit in AGC's common-fixed memory.
        file_size_word = int(os.path.getsize(bin_path) / 2)
        if file_size_word > 36 * self.mem.fixed_words:
            raise ValueError("File size is too big for core memory.")

        with open(bin_path, "rb") as f:

            addr = 0

            # Create a list corresponding to bank indexes 0 to 35
            banks = [i for i in range(36)]

            # yaYUL orders the banks in the bin file as 2, 3, 0, 1, 4, ..., 35.
            # So we need to reorder the first 4 elements of this list.
            banks[0], banks[1], banks[2], banks[3] = 2, 3, 0, 1

            banks_iter = iter(banks)
            bank = next(banks_iter)

            for i in range(file_size_word):

                # When we have filled one bank we go to the next one.
                if addr == self.mem.fixed_words:
                    try:
                        bank = next(banks_iter)
                    except StopIteration:
                        print("Core rope is larger than AGC's core memory.")

                    # We changed bank so we reset the address in this bank.
                    addr = 0

                # Read 2 bytes at a time.
                bytes = f.read(2)

                # Convert the bytes into a word
                word = int.from_bytes(bytes, byteorder='big')

                # Check if there is a parity bit set
                parity = word & 1

                # Convert the 16-bit word to 15 bits and add it into memory
                self.mem[bank, addr, 'fixed'] = word >> 1

                # No idea what that does, taken from yaAGC.
                # TODO: Investigate why / 32 and % 32.
                self.parities[int((bank * self.mem.fixed_words + addr) / 32)] \
                    |= parity << (addr % 32)

                # If parity bits set we enable parity checking.
                if parity and not self.check_parity_flag:
                    self.check_parity_flag = True

                addr += 1

    def cpu_reset(self) -> None:

        # Initialise erasable memory.
        self.mem.switched = np.zeros(
            (self.mem.switched_banks, self.mem.erasable_words), dtype=np.int16)
        self.mem.unswitched = np.squeeze(np.reshape(
            self.mem.switched[0:3], (1, self.mem.erasable_words * 3)))
        self.mem[self.reg.Z, 'erasable']

        # Initialise I/O channels.
        self.io = _IO_channels(
            self.mem[self.reg.L:self.reg.L+1, 'erasable'],
            self.mem[self.reg.Q:self.reg.Q+1, 'erasable'])

        # Initialise the various flags and state variables.
        self.extracode_flag = False
        # Should the check_parity_flag stay the same after a reset if we keep
        # the current ROM in memory?
        self.check_parity_flag = False
        self.irq.enable = True


cpu = Cpu()
cpu.load_core_rope("test.agc.bin")
# cpu.run()
