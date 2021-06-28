# from time import monotonic_ns as time_ns
# from time import process_time_ns as time_ns
# from time import time_ns as time_ns
# from time import thread_time_ns as time_ns
from time import perf_counter_ns as time_ns


class _Timer:
    def __init__(self) -> None:

        self.MCT_ns = 11720  # Machine cycle : 11.72 µs
        self.elapsed_time_ns = 0
        self.cycle_start_time_ns = time_ns()
        self.added_cycle = 0  # For instructions taking more than 1 MCT
        self.elapsed_time = 0

    def wait_cycle(self, nb_cycle: int = 1) -> None:

        start_wait = time_ns()

        while True:

            elapsed_wait = (time_ns() - start_wait)

            if elapsed_wait >= self.MCT_ns * nb_cycle:
                #print(elapsed_wait * 1e-3)
                break

    def do_cycle(self) -> bool:

        self.elapsed_time_ns = (time_ns() - self.cycle_start_time_ns)

        if self.elapsed_time_ns >= self.MCT_ns + (self.MCT_ns *
                                                  self.added_cycle):

            print("do_cycle: " + str(self.elapsed_time_ns * 1e-3))
            self.cycle_start_time_ns = time_ns()

            if self.added_cycle > 0:
                self.added_cycle = 0

            return True
        else:
            return False
