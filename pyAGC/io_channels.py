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

import numpy as np

# I/O channels: Addresses range: 0o000 to 0o777
# Channels 1 and 2 overlap the L and Q registers
# We pass a view of memory register L and Q to the IO memory
# Any update done on L and Q will updated channel 1 and 2


class _IO_channels:
    def __init__(self, L: np.ndarray, Q: np.ndarray) -> None:

        # Note: We cannot do self.channel[0] = np.squeeze(L)
        # Numpy will create a copy instead of keeping the view
        self.channel = np.zeros((0o1000))
        self.channel1 = np.squeeze(L)
        self.channel2 = np.squeeze(Q)

        # Channel 0o32 is to indicate that the PRO (STBY) key is being pressed.
        # No idea about the other.
        # TODO: Research what are channels 0o30, 0o31, 0o33 and why 0o37777.
        for i in range(0o30, 0o34):
            self.channel[i] = 0o37777
