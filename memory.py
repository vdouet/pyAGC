# https://www.ibiblio.org/apollo/assembly_language_manual.html#CPU_Architecture_Registers
# https://www.ibiblio.org/apollo/MirkoMattioliMemoryMap.pdf

import numpy as np

# All addresses are represented as octal not binary.

# Machine cycle : 11.72 µs
# CPU frequency 2.048 MHz (?) divided into different clock timings

# I/O channels: Addresses range: 0o000 to 0o777
# Channels 1 and 2 overlap the L and Q registers
# We pass a view of memory register L and Q to the IO memory
# Any update done on L and Q will updated channel 1 and 2
class _IO_channels:
    def __init__(self, L:np.ndarray, Q:np.ndarray) -> None:

        # Note: We cannot do self.memory[0] = np.squeeze(L)
        # Numpy will create a copy instead of keeping the view
        self.memory = np.zeros((0o1000))
        self.channel1 = np.squeeze(L)
        self.channel2 = np.squeeze(Q)

class _Interrupts:
    def __init__(self) -> None:

        # https://www.ibiblio.org/apollo/assembly_language_manual.html#Interrupt_Processing

        # Name: BOOT
        # Trigger: Power-up or GOJ signal.
        # Desc: This is where the program begins executing at power-up, and where hardware resets cause execution to go.
        self.BOOT = 0o4000

        # Name: T6RUPT
        # Trigger: Counter-register TIME6 decremented to 0.
        # Desc: The digital autopilot (DAP) for controlling thrust times of the jets of the reaction control system (RCS).
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
        # Desc:
        self.T4RUPT = 0o4020

        # Name:
        # Trigger:
        # Desc:
        self.KEYRUPT1 = 0o4024

        # Name:
        # Trigger:
        # Desc:
        self.KEYRUPT2 = 0o4030

        # Name:
        # Trigger:
        # Desc:
        self.UPRUPT = 0o4034

        # Name:
        # Trigger:
        # Desc:
        self.DOWNRUPT = 0o4040

        # Name:
        # Trigger:
        # Desc:
        self.RADARRUPT = 0o4044

        # Name:
        # Trigger:
        # Desc:
        self.HANDRUPT = 0o4050

class _Registers:
    def __init__(self) -> None:

        # Definition of the registers addresses - Using octal representation
        # All are 15 bits registers except otherwise specified
        # When a register is 16 bits the last bit is used to detect overflow/underflow

        # Register A "Accumulator" - 16 bits
        self.A = 0o00

        # Register L
        self.L = 0o01

        # Register Q stores return addresses of called procedures
        self.Q = 0o02

        # Register EB "Erasable Bank register" 000 0EE E00 000 000 - EEE are the bank selector bits
        self.EB = 0o03

        # Register FB "Fixed Bank register" FFF FF0 000 000 000 supplemented by a 7th bit from i/o channel 7 ("superbank bit")
        self.FB = 0o04

        # Register Z Program-counter register
        # Indicated the next instruction to be executed, always updated prior to executing the instruction
        # 12-bits register combined with EEE (from EB) and FFFFF (from FB) + superbank bit
        self.Z = 0o05

        # Register BB "Both Bank register" duplicates bits from EB and FB: FFF FF0 000 000 EEE
        # Changes to this register affect EB and FB
        self.BB = 0o06

        # Unnamed register, always as the value 00000
        self.UNNAMED_REG1 = 0o07

        # Register ARUPT - Location to store the value of A during an interrupt service routine
        self.ARUPT = 0o10

        # Register LRUPT - Location to store the value of L during an interrupt service routine
        self.LRUPT = 0o11

        # Register QRUPT - Location to store the value of Q during an interrupt service routine
        self.QRUPT = 0o12

        # Registers used to store copies of TIME1 and TIME2
        # Don't know if I should declare two registers
        # in the website it is declared as one "SAMPTIME" using addresses 13 and 14
        self.SAMPTIME1 = 0o13
        self.SAMPTIME2 = 0o14

        # Register ZRUPT - Stores the return address + 1 of an interrupt service routine (from Z)
        self.ZRUPT = 0o15

        # Register BBRUPT - Location to store the value of BB during an interrupt service routine
        self.BBRUPT = 0o16

        # Register BRUPT - Stores the value stored at the return address of an interrupt service routine
        self.BRUPT = 0o17

        # Register CYR "CYcle Right register" - When a value is written, right cycle it
        # Ex: abc def ghi jkl mno -> oab cde fgh ijk lmn
        self.CYR = 0o20

        # Register SR "Shift Right register" - When a value is written, right shift it
        # Ex: abc def ghi jkl mno -> aab cde fgh ijk lmn
        self.SR = 0o21

        # Register CYL "CYcle Left register" - When a value is read, left cycle it
        # Ex: abc def ghi jkl mno -> bcd efg hij klm noa
        self.CYL = 0o22

        # Register EDOP "Edit Polish Opcode Register" used by the interpreter for decoding interpreted instructions
        # When a value is written, shift right 7 position and zeroe the upper 8 bits
        # Ex: abc def ghi jkl mno -> 000 000 00b cde fgh
        self.EDOP = 0o23

        # Registers TIME1 and TIME2
        # TIME1 15 bits 1's-complement counter incremented every 10 ms
        # When TIME1 overflow, TIME2 (14 bits) is incremented
        # TIME1/TIME2 can keep time for a bit over 31 days and act as the AGC's master clock
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
        # When counter reach +-0, interrupt T6RUPT is requested and then disable TIME6.
        # The T6RUPT is used by the digital autopilot (DAP) of the LM to control the jets of the reaction control system (RCS).
        self.TIME6 = 0o31

        # Registers CDUX, CDUY, CDUZ
        # Used to monitor the orientation of the spacecraft
        # CDUX refers to the "inner" gimbal angle, CDUY refers to the "middle" gimbal angle, and CDUZ refers to the "outer" gimbal angle.
        # Used like ADC to convert the analog angles from the gimbal
        # 5-bit 2's-complement unsigned values, angles are increased by 1 unit using PCDU and decreased using MCDU
        self.CDUX = 0o32
        self.CDUY = 0o33
        self.CDUZ = 0o34

        # Registers OPTY, OPTX
        # Monitor the orientation of the optics subsystem/LM rendezvous radar
        # OPTY for trunnion angle, OPTX for shaft angle, used like ADC
        # 5-bit 2's-complement unsigned values, angles are increased by 1 unit using PCDU and decreased using MCDU
        self.OPTY = 0o35
        self.OPTX = 0o36

        # Register PIPAX, PIPAY, PIPAZ "Pulsed Integrating Pendulous Accelerometer"
        # Velocity of the spacecraft on the 3 axis
        # Incremented or decremented with PINC or MINC
        self.PIPAX = 0o37
        self.PIPAY = 0o40
        self.PIPAZ = 0o41

        # Registers Q-RHCCTR (RHCP) "Pitch", P-RHCCTR (RHCY) "Yaw", R-RHCCTR (RHCR) "Roll"
        # LM Only
        # count in 1's-complement format, indicating the displacement of the rotational hand controller (RHC) in the pitch, yaw, or roll axes
        # Need to be adapted to be controlled by a joystick in simulation
        self.RHCP = 0o42
        self.RHCP = 0o43
        self.RHCP = 0o44

        # Register INLINK
        # Used to receive digital uplink data from a ground station
        # UPRUPT interrupt-request is set after a data word is received
        # Correct data is either "0" or he triply-redundant bit pattern
        # cccccCCCCCccccc, where CCCCC is meant to be the logical complement of ccccc , it is always a DSKY-type keycode
        self.INLINK = 0o45

        # Register RNRAD
        # Used for ?
        self.RNRAD = 0o46

        # Register GYROCTR (GYROCMD)
        # Used during IMU fine alignment to torque the gyro to the the precise alignment expected by the AGS
        self.GYROCTR = 0o47

        # Registers CDUXCMD, CDUYCMD, CDUYCMD
        # Used during IMU coarse alignment to drive the IMU stable platform to approximately the orientation expected by the AGC
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

class Memory:
    def __init__(self) -> None:

        # Definition of the memory used by the AGC
        # Read-only memory is called "fixed", read-write is called "erasable"
        # Unswitched memory can be directly addressable via an address
        # Switched memory addressable only via an address plus a bank number
        # (i/o channels not included in unswitched/switched)

        # Memory map (addresses in octal):
        # 0000-1377: Unswitched erasable (Addressable using register Z)
        # 1400-1777: Switched erasable (Addressable using register Z + EB)
        # 2000-3777: Common fixed (Addressable using register Z + FB and superbank bit)
        # 4000-7777: Fixed fixed (Addressable using register Z)

        # Unswitched-erasable memory overlaps with banks E0, E1, and E2 of switched-erasable memory
        # I/O channels also overlap the unswitched-erasable memory
        # Note to self for the Memory Map schema:
        # There are 0o400 (256) words but addressing in octal are only possible as:
        # 0o000 (0) -> 0o377 (255), 0o400 (256) -> 0o777 (511), etc.
        self.erasable_words = 0o400
        self.switched_banks = 8
        self.switched = np.zeros((self.switched_banks, self.erasable_words))

        # Create unswitched memory that shares memory with the switched one
        # We take the same memory space as the first 3 banks and squeeze it into a 1D array
        # This way we can directly address the unswitched memory and use the memory-bank selection
        # registers to access the switched memory:
        # unswitched[addr]
        # switched[banks][addr]
        # If we modify unswitched it would also modify switched.
        # The same is true for unswitched if we modify the shared memory space of switched
        self.unswitched = np.squeeze(np.reshape(self.switched[0:3], (1, self.erasable_words * 3)))

        # Common fixed and fixed fixed memory also overlap
        # AGC could address 40 banks of fixed memory but only 36 where physically implemented and used
        # yaAGC actually uses these extra banks but only contain 0, we will do the same
        self.fixed_words = 0o2000
        self.common_fixed_banks = 40
        self.common_fixed = np.zeros((self.common_fixed_banks, self.fixed_words))

        # Same a unswitched memory there is an overlap between banks 2 and 3 of common fixed memory
        # and fixed fixed memory. We just take the memory overlap's addresses and reference them in
        # another array for simplicity. We can access both memories like:
        # fixed_fixed[addr]
        # common_fixed[banks+FEB][addr]
        self.fixed_fixed = np.squeeze(np.reshape(self.common_fixed[2:4], (1, self.fixed_words * 2)))

        # Erasable and switched memory flatten to represent the addresses implemented in hardware
        # TODO: fixed_hrdwr_memory doesn't represent the true hardware addresses. Due to the fact that
        # cpu addresses for fixed fixed (and 2, 3 overlap) start at 0o4000 and cpu addresses for
        # the common fixed mem start at 0o2000. When we reshape and flatten it means the memory
        # will keep it's cpu addresses order that is not the same as the hardware addresses one
        # TODO: Maybe replace that with a single array for hardware memory and a method that copy values
        # from the original arrays rather than trying to manipulated array refererences
        self.erasable_hrdwr_memory = np.squeeze(np.reshape(self.switched, (1, self.erasable_words * self.switched_banks)))
        self.fixed_hrdwr_memory = np.squeeze(np.reshape(self.common_fixed, (1, self.fixed_words * self.common_fixed_banks)))

        # I/O Channels
        # Slicing a numpy array creates a view on the original array. This is done because of the
        # channel 1 and 2 overlap with register L and Q
        self.io_channels = _IO_channels(self.unswitched[self.L:self.L+1], self.unswitched[self.Q:self.Q+1])

        # Registers
        self.reg = _Registers()

        # Using __getitem__ and __setitem__ all work
        # on erasable and fixed memory is handled internally
        # in this class.
        # This will make the main CPU loop more understandable
        # than handling all the different memories there.

        # This method is used to read data from memory.
        def __getitem__(self, key):
            pass

        # This method is used to write to memory
        def __setitem__(self, key, value):
            pass


mem = Memory()

#print(reg.erasable_mem)
#print("\n\n")
#print(reg.unswitched_mem)
#print(len(reg.unswitched_mem))
#for i in range(len(reg.unswitched_mem)):
#    for j in range(len(reg.unswitched_mem[0])):
#        reg.unswitched_mem[i][j] = 1

#for i in range(len(reg.unswitched_mem)):
#    reg.unswitched_mem[i] = 1


#reg.switched_mem[0][0] = 0b111110000011000
#print("\n\n")
#print(reg.unswitched_mem)
#print(len(reg.unswitched_mem))
#print("\n\n")
#print(reg.switched_mem)


# Maybe do something like this if read/write methods are really different between registers?
# This is called "Composition", Register_test is a composite of components Register_A and Register_B
# If multiple register uses the same read/write methods we can make them inherit them I guess (the read/write methods).
class Register_A:
    def __init__(self):
        self.addr = 0o01

    def read(self):
        print("read A")

class Register_B:
    def __init__(self):
        self.addr = 0o02

    def read(self):
        print("read B")

class Register_test:
    def __init__(self):
        self.memory = []
        self.A = Register_A()
        self.B = Register_B()

#reg = Register_test()
#reg.A.read()
#reg.B.read()