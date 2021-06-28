from registers import _Registers
from memory import _Memory
from io_channels import _IO_channels
from interrupts import _Interrupts
from timer import _Timer

from time import perf_counter_ns as time_ns

from timeit import default_timer as timer



class Cpu:
    def __init__(self) -> None:

        self.flag_extracode = False

        self.timer = _Timer()
        self.reg = _Registers()
        self.mem = _Memory(self.reg)
        self.irq = _Interrupts(self.mem, self.reg)

    def run(self) -> None:

        start = time_ns()

        while True:

            # Execute a CPU cycle every 11.72 µs or more depending on the
            # number of MCT taken by instructions
            if self.timer.do_cycle():

                print("run: " + str((time_ns() - start) * 1e-3))
                start = time_ns()
                self._execute_cycle()
                #print(self.timer.elapsed_time_ns * 1e-3)

    def _execute_cycle(self) -> None:
        #self.timer.wait_cycle()
        self.timer.added_cycle = 1
        pass


cpu = Cpu()
cpu.run()