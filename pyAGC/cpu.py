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

import numpy as np

from timer import _Timer
from memory import _Memory
from registers import _Registers
from interrupts import _Interrupts
from io_channels import _IO_channels
from _cpu_utils import _load_core_rope


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
        """Method that calls _load_core_rope() to load provided .bin file
        into AGC's memory.

        Args:
            bin_path (str): Path to the .bin file to load.
        """

        _load_core_rope(bin_path, self.mem, self.check_parity_flag,
                        self.parities)

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
