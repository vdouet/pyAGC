import numpy as np

# I/O channels: Addresses range: 0o000 to 0o777
# Channels 1 and 2 overlap the L and Q registers
# We pass a view of memory register L and Q to the IO memory
# Any update done on L and Q will updated channel 1 and 2


class _IO_channels:
    def __init__(self, L: np.ndarray, Q: np.ndarray) -> None:

        # Note: We cannot do self.memory[0] = np.squeeze(L)
        # Numpy will create a copy instead of keeping the view
        self.memory = np.zeros((0o1000))
        self.channel1 = np.squeeze(L)
        self.channel2 = np.squeeze(Q)
