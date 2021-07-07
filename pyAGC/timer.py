"""Copyright (C) 2021  Victor Douet

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

# from time import monotonic_ns as time_ns
# from time import process_time_ns as time_ns
# from time import time_ns as time_ns
# from time import thread_time_ns as time_ns
from time import perf_counter_ns as time_ns


# FIXME: This timing class tried the latest available timers from the time
# module but precision is still inconsistent, though one cycle precision is
# still quite accurate on MacOS but horrible on Windows. But reaching precise
# accurate microsecond precision is not simple.
class _Timer:
    def __init__(self) -> None:

        self.MCT_ns = 11720  # Machine cycle : 11.72 µs
        self.elapsed_time_ns = 0
        self.cycle_start_time_ns = time_ns()

        # For instructions taking more than 1 MCT
        self.added_cycle = 0
        self.elapsed_wait = 0

        self.total_cycle_time = 0

    def wait_cycle(self, nb_cycle: int = 1) -> None:

        start_wait = time_ns()

        while self.elapsed_wait < self.MCT_ns * nb_cycle:
            self.elapsed_wait = (time_ns() - start_wait)

    def do_cycle(self) -> bool:

        # We take into account the cycle(s) or wait time added by the
        # instructions:

        # elapsed_wait is used to wait the number of cycles requested directly
        # after the instruction so we remove the time taken by it from the
        # original elapsed cycle.
        self.elapsed_time_ns = (time_ns() - self.elapsed_wait) - \
            self.cycle_start_time_ns

        # added_cycle is here to simulate spent MCT at the end of the cpu cycle
        # ie. We do the instructions, we continue the code and then at the end
        # we wait the number of cycles requested (added to the original MCT).
        if self.elapsed_time_ns >= self.MCT_ns + \
                (self.MCT_ns * self.added_cycle):

            self.cycle_start_time_ns = time_ns()

            # We reset the added cycle(s) after use
            if self.added_cycle > 0:
                self.added_cycle = 0

            # We calculate the total elapsed time of the CPU + Instructions
            self.total_cycle_time = self.elapsed_time_ns + self.elapsed_wait

            # We reset the elapsed time during wait after use
            if self.elapsed_wait > 0:
                self.elapsed_wait = 0

            return True

        else:
            return False
