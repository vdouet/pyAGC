from registers import _Registers
from memory import _Memory
from io_channels import _IO_channels
from interrupts import _Interrupts
from timer import _Timer

from time import perf_counter_ns as time_ns


class Cpu:
    def __init__(self) -> None:

        self.flag_extracode = False

        self.timer = _Timer()
        self.reg = _Registers()
        self.mem = _Memory(self.reg)
        self.irq = _Interrupts(self.mem, self.reg)

    def run(self) -> None:

        wait_time = 0

        while True:

            # Execute a CPU cycle every 11.72 µs or more depending on the
            # number of MCT taken by instructions
            if self.timer.do_cycle():

                print("Loop time: " + str(self.timer.elapsed_time_ns * 1e-3))
                print("Total time: " + str(self.timer.total_cycle_time * 1e-3))
                self.timer.wait_cycle()
                print("Wait time: " + str((self.timer.elapsed_wait * 1e-3)))
                self.timer.added_cycle = 1


    def _execute_cycle(self) -> None:
        pass


cpu = Cpu()
cpu.run()