from registers import _Registers
from memory import _Memory
from io_channels import _IO_channels
from interrupts import _Interrupts

# Machine cycle : 11.72 µs
# CPU frequency 2.048 MHz (?) divided into different clock timings


class Cpu:
    def __init__(self) -> None:

        flag_extracode = False

        reg = _Registers()
        mem = _Memory(reg)
        irq = _Interrupts(mem, reg)

    def run(self):
        print("Running the CPU")


cpu = Cpu()
cpu.run()
