"""
Modified work Copyright (C) 2021  Victor Douet <victor.douet@gmail.com>
Original work Copyright 2003-2006,2009,2017 Ronald S. Burkey <info@sandroid.org>

Changes:
Original agc_load_binfile() function adapted and converted in Python for PyAGC.

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
import os


def load_core_rope(bin_path: str, mem: np.ndarray, check_parity_flag: bool,
                   parities: np.ndarray) -> None:
    """Method to load provided .bin file into AGC's memory.

    Mostly taken from agc_engine_init.c from yaAGC as I haven't explored
    how yaYUL function yet.

    Args:
        bin_path (str): Path to the .bin file to load.
        mem (np.ndarray): AGC's memory.
        check_parity_flag (bool): Flag regarding the parity flag.
        parities (np.ndarray): Array when parity is found in loaded .bin file.

    Raises:
        TypeError: if bin_path is null or not a str.
        FileNotFoundError: if bin_path does not point to an existing file.
        ValueError: if .bin file size is not even.
        ValueError: if .bin file size to big for AGC's memory.
    """

    # Check if the provided path is a string and not empty.
    if not isinstance(bin_path, str) or not bin_path:
        raise TypeError("Provided path is either empty or not a string.")

    # If the provided file does not end with the .bin extension, add it.
    if not bin_path.lower().endswith(".bin"):
        bin_path = bin_path + ".bin"

    # Check if file exist.
    if not os.path.isfile(bin_path):
        raise FileNotFoundError(f"Error: file does not exist '{bin_path}'")

    # File size should be an even number of bytes.
    if os.path.getsize(bin_path) % 2:
        raise ValueError("Incorrect file size (size is not even).")

    # File size should fit in AGC's common-fixed memory.
    file_size_word = int(os.path.getsize(bin_path) / 2)
    if file_size_word > 36 * mem.fixed_words:
        raise ValueError("File size is too big for core memory.")

    with open(bin_path, "rb") as f:

        addr = 0

        # Create a list corresponding to bank indexes 0 to 35
        banks = [i for i in range(36)]

        # yaYUL orders the banks in the bin file as 2, 3, 0, 1, 4, ..., 35.
        # So we need to reorder the first 4 elements of this list.
        banks[0], banks[1], banks[2], banks[3] = 2, 3, 0, 1

        banks_iter = iter(banks)
        bank = next(banks_iter)

        for i in range(file_size_word):

            # When we have filled one bank we go to the next one.
            if addr == mem.fixed_words:
                try:
                    bank = next(banks_iter)
                except StopIteration:
                    print("Core rope is larger than AGC's core memory.")

                # We changed bank so we reset the address in this bank.
                addr = 0

            # Read 2 bytes at a time.
            bytes = f.read(2)

            # Convert the bytes into a word
            word = int.from_bytes(bytes, byteorder='big')

            # Check if there is a parity bit set
            parity = word & 1

            # Convert the 16-bit word to 15 bits and add it into memory
            mem[bank, addr, 'fixed'] = word >> 1

            # No idea what that does, taken from yaAGC.
            # TODO: Investigate why / 32 and % 32.
            parities[int((bank * mem.fixed_words + addr) / 32)] \
                |= parity << (addr % 32)

            # If parity bits set we enable parity checking.
            if parity and not check_parity_flag:
                check_parity_flag = True

            addr += 1
