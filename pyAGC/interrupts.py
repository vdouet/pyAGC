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

# https://www.ibiblio.org/apollo/assembly_language_manual.html#Interrupt_Processing

import registers
import memory


class _Interrupts:
    def __init__(self, mem: memory._Memory, reg: registers._Registers) -> None:

        self.mem = mem
        self.reg = reg

        # Name: BOOT
        # Trigger: Power-up or GOJ signal.
        # Desc: This is where the program begins executing at power-up, and
        # where hardware resets cause execution to go.
        self.BOOT = 0o4000

        # Name: T6RUPT
        # Trigger: Counter-register TIME6 decremented to 0.
        # Desc: The digital autopilot (DAP) for controlling thrust times of the
        # jets of the reaction control system (RCS).
        self.T6RUPT = 0o4004

        # Name: T5RUPT
        # Trigger: Overflow of counter-timer TIME5.
        # Desc: Used by the autopilot.
        self.T5RUPT = 0o4010

        # Name: T3RUPT
        # Trigger: Overflow of counter-timer TIME3.
        # Desc: Used by the task scheduler (WAITLIST).
        self.T3RUPT = 0o4014

        # Name: T4RUPT
        # Trigger: Overflow of counter-timer TIME4.
        # Desc: Used for various DSKY-related activities such as monitoring the
        # PRO key and updating display data.
        self.T4RUPT = 0o4020

        # Name: KEYRUPT1
        # Trigger: Keystroke received from DSKY.
        # Desc: The DSKY transmits codes representing keystrokes to the AGC.
        # Reception of these codes by the AGC hardware triggers an interrupt.
        self.KEYRUPT1 = 0o4024

        # Name: KEYRUPT2
        # Trigger: Keystroke received from secondary DSKY.
        # Desc: A second DSKY is used in the CM at the navigator's station
        self.KEYRUPT2 = 0o4030

        # Name: UPRUPT
        # Trigger: Uplink word available in the INLINK register.
        # Desc: When a word has been assembled in AGC INLINK counter-register
        # an interrupt is triggered.
        self.UPRUPT = 0o4034

        # Name: DOWNRUPT
        # Trigger: The downlink shift register is ready for new data (output
        # channels 34 & 35).
        # Desc: Used for telemetry-downlink.
        self.DOWNRUPT = 0o4040

        # Name: RADARUPT
        # Trigger: Automatically generated inside the AGC after a set pulse
        # sequence has been sent to the radars.
        # Desc: Data from the rendezvous radar is assembled similarly to the
        # uplink data described above.
        # When a data word is complete, an interrupt is triggered.
        self.RADARRUPT = 0o4044

        # Name: HANDRUPT or RUPT10
        # Trigger: Selectable from three possible sources: Trap 31A, Trap 31B,
        # and Trap 32.
        # Desc: Used for the hand controller. Only trap 31A is ever used.
        # Trap 31-A (enabled by resetting CH13 bit 12): Causes a RUPT10 when
        # any of CH31 bits 1-6 are set.
        self.HANDRUPT = 0o4050
        self.RUPT10 = 0o4050

        # Enable or disable interrupt vectoring
        self.enable = True

    def process(self, intrpt: int) -> None:

        # TODO: Add more conditions when interrupt request is denied (extracode
        # flag, overflow/underflow, etc.)
        if self.enable:

            # 1. Save the content of the program counter (Z reg) into ZRUPT
            # NOTE: It says it is the return address + 1?
            self.mem[self.reg.ZRUPT] = self.mem[self.reg.Z]

            # 2. The instruction appearing at the memory location pointed to by
            # the program counter is saved into the BRUPT register.
            self.mem[self.reg.BRUPT] = self.mem[self.mem[self.reg.Z]]

            # 3. Control passes to the appropriate vector-table location
            self.reg.B = intrpt

            # 4. Execution then continues (with interrupts inhibited) until the
            # interrupt-service routine returns using the RESUME instruction.
            self.enable = False

            return True

        else:

            return False
