import numpy as np
from scipy.io import wavfile
from numba import njit, jit

@jit(forceobj=True)
def convert_to_raw(filename: str):
    rate, data = wavfile.read(filename)

    max_int16 = np.iinfo(np.int16).max
    max_val = data.max(axis=0)
    if max_val > max_int16:
        reduction_rate = max_int16 / max_val
        data = data * (reduction_rate)
    data = data.astype(np.int16)
    save_raw(filename, data)

def save_raw(filename, samples):
    with open(filename.replace(".wav", ".raw"),"wb") as f:
        f.write(samples.tobytes())
