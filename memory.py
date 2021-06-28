# https://www.ibiblio.org/apollo/MirkoMattioliMemoryMap.pdf

import numpy as np

import registers
from io_channels import _IO_channels


class _Memory:
    def __init__(self, reg: registers._Registers) -> None:

        # Registers
        self.reg = reg

        # All addresses are represented as octal not binary.

        # Definition of the memory used by the AGC
        # Read-only memory is called "fixed", read-write is called "erasable"
        # Unswitched memory can be directly addressable via an address
        # Switched memory addressable only via an address plus a bank number
        # (i/o channels not included in unswitched/switched)

        # Memory map (addresses in octal):
        # 0000-1377: Unswitched erasable (Addressable using register Z)
        # 1400-1777: Switched erasable (Addressable using register Z + EB)
        # 2000-3777: Common fixed (Addressable using register Z + FB and
        # superbank bit)
        # 4000-7777: Fixed fixed (Addressable using register Z)

        # Unswitched-erasable memory overlaps with banks E0, E1, and E2 of
        # switched-erasable memory
        # I/O channels also overlap the unswitched-erasable memory
        # Note to self for the Memory Map schema:
        # There are 0o400 (256) words but addressing in octal are only possible
        # as: 0o000 (0) -> 0o377 (255), 0o400 (256) -> 0o777 (511), etc.
        self.erasable_words = 0o400
        self.switched_banks = 8
        self.switched = np.zeros(
            (self.switched_banks, self.erasable_words), dtype=np.int16)

        # Create unswitched memory that shares memory with the switched one
        # We take the same memory space as the first 3 banks and squeeze it
        # into a 1D array
        # This way we can directly address the unswitched memory and use the
        # memory-bank selection registers to access the switched memory:
        # unswitched[addr]
        # switched[banks][addr]
        # If we modify unswitched it would also modify switched. The same is
        # true for unswitched if we modify the shared memory space of switched
        self.unswitched = np.squeeze(np.reshape(
            self.switched[0:3], (1, self.erasable_words * 3)))

        # Common fixed and fixed fixed memory also overlap
        # AGC could address 40 banks of fixed memory but only 36 where
        # physically implemented and used yaAGC actually uses these extra banks
        # but only contain 0, we will do the same
        self.fixed_words = 0o2000
        self.common_fixed_banks = 40
        self.common_fixed = np.zeros(
            (self.common_fixed_banks, self.fixed_words), dtype=np.int16)

        # Same a unswitched memory there is an overlap between banks 2 and 3 of
        # common fixed memory and fixed fixed memory. We just take the memory
        # overlap's addresses and reference them in another array for
        # simplicity. We can access both memories like:
        # fixed_fixed[addr]
        # common_fixed[banks+FEB][addr]
        self.fixed_fixed = np.squeeze(np.reshape(
            self.common_fixed[2:4], (1, self.fixed_words * 2)))

        # Erasable and switched memory flatten to represent the addresses
        # implemented in hardware
        # FIXME: fixed_hrdwr_memory doesn't represent the true hardware
        # addresses. Due to the fact that cpu addresses for fixed fixed (and 2,
        # 3 overlap) start at 0o4000 and cpu addresses for the common fixed mem
        # start at 0o2000. When we reshape and flatten it means the memory
        # will keep it's cpu addresses order that is not the same as the
        # hardware addresses one
        # TODO: Maybe replace that with a single array for hardware memory and
        # a method that copy values from the original arrays rather than trying
        # to manipulated array refererences
        self.erasable_hrdwr_memory = np.squeeze(np.reshape(
            self.switched, (1, self.erasable_words * self.switched_banks)))
        self.fixed_hrdwr_memory = np.squeeze(np.reshape(
            self.common_fixed,
            (1, self.fixed_words * self.common_fixed_banks)))

        # I/O Channels
        # Slicing a numpy array creates a view on the original array. This is
        # done because of the channel 1 and 2 overlap with register L and Q
        # NOTE: Should the IO be outside of the memory class?
        self.io_channels = _IO_channels(
            self.unswitched[self.reg.L:self.reg.L+1],
            self.unswitched[self.reg.Q:self.reg.Q+1])

    # Using __getitem__ and __setitem__ all work
    # on erasable and fixed memory is handled internally
    # in this class. This will make the main CPU loop more understandable
    # than handling all the different memories there.

    # This method is used to read data from memory.
    def __getitem__(self, loc):

        # We check if we want to access switched or common-fixed memory
        # by passing a block number.
        if isinstance(loc, tuple):
            block, addr = loc
        else:
            addr = loc

        if addr < 0o1400:
            return self.unswitched[addr]

    # This method is used to write to memory
    def __setitem__(self, loc, value):

        if isinstance(loc, tuple):
            block, addr = loc
        else:
            addr = loc

        if addr < 0o1400:
            self.unswitched[addr] = value
