# https://www.ibiblio.org/apollo/assembly_language_manual.html#CPU_Architecture_Registers

import numpy as np


class _Registers:
    def __init__(self) -> None:

        # Definition of the registers addresses - Using octal representation
        # All are 15 bits registers except otherwise specified
        # When a register is 16 bits the last bit is used to detect
        # overflow/underflow

        # Register A "Accumulator" - 16 bits
        self.A = 0o00

        # Register L
        self.L = 0o01

        # Register Q stores return addresses of called procedures
        self.Q = 0o02

        # Register EB "Erasable Bank register" 000 0EE E00 000 000 - EEE are
        # the bank selector bits
        self.EB = 0o03

        # Register FB "Fixed Bank register" FFF FF0 000 000 000 supplemented by
        # a 7th bit from i/o channel 7 ("superbank bit")
        self.FB = 0o04

        # Register Z Program-counter register
        # Indicated the next instruction to be executed, always updated prior
        # to executing the instruction
        # 12-bits register combined with EEE (from EB) and FFFFF (from FB) +
        # superbank bit
        self.Z = 0o05

        # Register BB "Both Bank register" duplicates bits from EB and
        # FB: FFF FF0 000 000 EEE
        # Changes to this register affect EB and FB
        self.BB = 0o06

        # Unnamed register, always as the value 00000
        self.UNNAMED_REG1 = 0o07

        # Register ARUPT - Location to store the value of A during an interrupt
        # service routine
        self.ARUPT = 0o10

        # Register LRUPT - Location to store the value of L during an interrupt
        # service routine
        self.LRUPT = 0o11

        # Register QRUPT - Location to store the value of Q during an interrupt
        # service routine
        self.QRUPT = 0o12

        # Registers used to store copies of TIME1 and TIME2
        # Don't know if I should declare two registers, in the website it is
        # declared as one "SAMPTIME" using addresses 13 and 14
        self.SAMPTIME1 = 0o13
        self.SAMPTIME2 = 0o14

        # Register ZRUPT - Stores the return address + 1 of an interrupt
        # service routine (from Z)
        self.ZRUPT = 0o15

        # Register BBRUPT - Location to store the value of BB during an
        # interrupt service routine
        self.BBRUPT = 0o16

        # Register BRUPT - Stores the value stored at the return address of an
        # interrupt service routine
        self.BRUPT = 0o17

        # Register CYR "CYcle Right register" - When a value is written, right
        # cycle it. Ex: abc def ghi jkl mno -> oab cde fgh ijk lmn
        self.CYR = 0o20

        # Register SR "Shift Right register" - When a value is written, right
        # shift it. Ex: abc def ghi jkl mno -> aab cde fgh ijk lmn
        self.SR = 0o21

        # Register CYL "CYcle Left register" - When a value is read, left cycle
        # it. Ex: abc def ghi jkl mno -> bcd efg hij klm noa
        self.CYL = 0o22

        # Register EDOP "Edit Polish Opcode Register" used by the interpreter
        # for decoding interpreted instructions.
        # When a value is written, shift right 7 position and zeroe the upper
        # 8 bits. Ex: abc def ghi jkl mno -> 000 000 00b cde fgh
        self.EDOP = 0o23

        # Registers TIME1 and TIME2
        # TIME1 15 bits 1's-complement counter incremented every 10 ms
        # When TIME1 overflow, TIME2 (14 bits) is incremented TIME1/TIME2 can
        # keep time for a bit over 31 days and act as the AGC's master clock
        self.TIME2 = 0o24
        self.TIME1 = 0o25

        # Register TIME3
        # Similar to TIME1. When overflow occurs interrupt T3RUPT is requested
        # T3RUPT is used by the "wait-list" for scheduling multi-tasking.
        self.TIME3 = 0o26

        # Register TIME4 (increments 7.5 ms after TIME3)
        # Similar to TIME1. When overflow occurs interrupt T4RUPT is requested
        # T4RUPT is used for DSKY's display
        self.TIME4 = 0o27

        # Register TIME5 (increments 5 ms out of phase with TIME1 and TIME3)
        # Similar to TIME1. When overflow occurs interrupt T5RUPT is requested
        # T5RUPT is used by the DAP (digital autopilot)
        self.TIME5 = 0o30

        # Register TIME6
        # 15 bits 1's-complement updated every 1/1600 seconds by DINC
        # Enabling counting by writing 1 to bit 15 of i/o 13
        # Disabled counting by writing 0 to bit 15 of i/o 13
        # When counter reach +-0, interrupt T6RUPT is requested and then
        # disable TIME6.
        # The T6RUPT is used by the digital autopilot (DAP) of the LM to
        # control the jets of the reaction control system (RCS).
        self.TIME6 = 0o31

        # Registers CDUX, CDUY, CDUZ
        # Used to monitor the orientation of the spacecraft
        # CDUX refers to the "inner" gimbal angle, CDUY refers to the "middle"
        # gimbal angle, and CDUZ refers to the "outer" gimbal angle.
        # Used like ADC to convert the analog angles from the gimbal
        # 5-bit 2's-complement unsigned values, angles are increased by 1 unit
        # using PCDU and decreased using MCDU
        self.CDUX = 0o32
        self.CDUY = 0o33
        self.CDUZ = 0o34

        # Registers OPTY, OPTX
        # Monitor the orientation of the optics subsystem/LM rendezvous radar
        # OPTY for trunnion angle, OPTX for shaft angle, used like ADC
        # 5-bit 2's-complement unsigned values, angles are increased by 1 unit
        # using PCDU and decreased using MCDU
        self.OPTY = 0o35
        self.OPTX = 0o36

        # Register PIPAX, PIPAY, PIPAZ "Pulsed Integrating Pendulous
        # Accelerometer"
        # Velocity of the spacecraft on the 3 axis
        # Incremented or decremented with PINC or MINC
        self.PIPAX = 0o37
        self.PIPAY = 0o40
        self.PIPAZ = 0o41

        # Registers Q-RHCCTR (RHCP) "Pitch", P-RHCCTR (RHCY) "Yaw", R-RHCCTR
        # (RHCR) "Roll"
        # LM Only
        # count in 1's-complement format, indicating the displacement of the
        # rotational hand controller (RHC) in the pitch, yaw, or roll axes
        # Need to be adapted to be controlled by a joystick in simulation
        self.RHCP = 0o42
        self.RHCP = 0o43
        self.RHCP = 0o44

        # Register INLINK
        # Used to receive digital uplink data from a ground station
        # UPRUPT interrupt-request is set after a data word is received
        # Correct data is either "0" or he triply-redundant bit pattern
        # cccccCCCCCccccc, where CCCCC is meant to be the logical complement of
        # ccccc , it is always a DSKY-type keycode
        self.INLINK = 0o45

        # Register RNRAD
        # Used for ?
        self.RNRAD = 0o46

        # Register GYROCTR (GYROCMD)
        # Used during IMU fine alignment to torque the gyro to the the precise
        # alignment expected by the AGS
        self.GYROCTR = 0o47

        # Registers CDUXCMD, CDUYCMD, CDUYCMD
        # Used during IMU coarse alignment to drive the IMU stable platform to
        # approximately the orientation expected by the AGC
        self.CDUXCMD = 0o50
        self.CDUYCMD = 0o51
        self.CDUZCMD = 0o52

        # Registers OPTYCMD, OPTXCMD
        # Used for ?
        self.OPTYCMD = 0o53
        self.OPTXCMD = 0o54

        # Register THRUST
        # LM only
        self.THRUST = 0o55

        # Register LEMONM
        # LM only
        self.LEMONM = 0o56

        # Register OUTLINK
        # Apparently unused
        self.OUTLINK = 0o57

        # Register ALTM
        # LM only
        self.ALTM = 0o60

        # TODO: Apparently an hidden "B" register is used to store the next
        # instruction when INDEX is processed. Maybe find its address in
        # memory?
        self.B = np.int16(0)
