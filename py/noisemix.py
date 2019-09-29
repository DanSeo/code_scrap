import numpy as np
from scipy.io import wavfile
from numba import njit, jit
from time import perf_counter
import os
from functools import lru_cache
"""
need numba, 
numba-numpy 
numba-scipy
"""

MAX_LRU_CACHE_SIZE=1000

@njit(fastmath=True)
def calculate_adjusted_rms(clean_rms, snr):
    a = float(snr) / 20
    noise_rms = clean_rms / (10**a)
    return noise_rms

@jit(forceobj=True)
def load_wavefile(filename: str):
    rate, amptitude = wavfile.read(filename)
    return rate, amptitude

@lru_cache(maxsize=MAX_LRU_CACHE_SIZE)
@jit(forceobj=True)
def load_noise_wavefile(filename: str):
    rate, amptitude = wavfile.read(filename)
    return rate, amptitude

@jit(forceobj=True)
def calculate_rms(amp):
    return np.sqrt(np.mean(np.square(amp), axis=-1))


def save_waveform(output_path, rate, amp):
    wavfile.write(output_path, rate ,amp)

@jit(forceobj=True)
def mix_noise(clean_filename, noise_filename, snr):
    c_rate, clean_amp = load_wavefile(clean_filename)
    n_rate, noise_amp = load_noise_wavefile(noise_filename)
    clean_rms = calculate_rms(clean_amp)

    start = np.random.randint(0, len(noise_amp) - len(clean_amp))

    divided_noise_amp = split_noise(clean_amp, noise_amp, start)
    noise_rms = calculate_rms(divided_noise_amp)
    adjusted_noise_rms = calculate_adjusted_rms(clean_rms, snr)

    mixed_amp = mix(adjusted_noise_rms, clean_amp, divided_noise_amp, noise_rms)
    mixed_amp = normalize_mixed_amp(mixed_amp)

    return start, c_rate, mixed_amp


@jit(forceobj=True)
def save_mix_noise(clean_filename, noise_filename, savefilename, snr) -> int:
    start, rate, mixed = mix_noise(clean_filename, noise_filename, snr)

    save_waveform(savefilename, rate, mixed)
    return start

@njit
def split_noise(clean_amp, noise_amp, start):
    divided_noise_amp = noise_amp[start: start + len(clean_amp)]
    return divided_noise_amp


@jit(forceobj=True)
def normalize_mixed_amp(mixed_amp):
    max_int16 = np.iinfo(np.int16).max
    mixed_amp_max_val = mixed_amp.max(axis=0)
    if mixed_amp_max_val > max_int16:
        reduction_rate = max_int16 / mixed_amp_max_val
        mixed_amp = mixed_amp * (reduction_rate)
    return mixed_amp


@njit
def mix(adjusted_noise_rms, clean_amp, divided_noise_amp, noise_rms):
    adjusted_noise_amp = divided_noise_amp * (adjusted_noise_rms / noise_rms)
    mixed_amp = (clean_amp + adjusted_noise_amp)
    return mixed_amp


@jit(parallel=True)
def mix_noises(clean_files, noise_files, save_files, snr):
    noise_starts = np.zeros((len(clean_files)))
    for idx, clean in enumerate(clean_files):
        noise = noise_files[idx]
        save_fn = save_files[idx]

        noise_starts[idx] = save_mix_noise(clean, noise, save_fn, snr)
    return noise_starts


@jit(parallel=True)
def mix_random_noises(clean_files, noise_files, save_files, snr):
    noise_start_noise_indexes = np.zeros((len(clean_files), 2))
    rand_noise_idxs = np.random.randint(0, len(noise_files) - 1, len(clean_files))
    for idx, clean in enumerate(clean_files):
        noise_idx = rand_noise_idxs[idx]
        noise = noise_files[noise_idx]
        save_fn = save_files[idx]

        noise_start_noise_indexes[idx][0] = save_mix_noise(clean, noise, save_fn, snr)
        noise_start_noise_indexes[idx][1] = noise_idx
    return noise_start_noise_indexes


@jit(parallel=True, forceobj=True)
def mix_random_noises_snrs(clean_files, noise_files, save_files, snrs):
    noise_start_noise_indexes = []
    length = len(clean_files)
    rand_noise_idxs = np.random.randint(0, len(noise_files) - 1, length)
    rand_snrs_idxs = np.random.randint(0, len(snrs) - 1, length)

    for idx, clean in enumerate(clean_files):
        noise_idx = rand_noise_idxs[idx]
        snr_idx = rand_snrs_idxs[idx]
        snr = snrs[snr_idx]
        noise = noise_files[noise_idx]
        save_fn = save_files[idx]
        noise_start = save_mix_noise(clean, noise, save_fn, snr)
        noise_start_noise_indexes.append([
            int(noise_start),
            noise_idx,
            snr_idx
        ])
    return np.array(noise_start_noise_indexes, dtype=int)


def mix_noise_lists(clean_files,
                    noise_files,
                    output_filenames,
                    snrs_or_snr,
                    mode="random_noise_snrs"):
    mix_results = np.array([np.array([0, 0, 0], dtype=int) for i in range(len(clean_files))], dtype=int)

    if mode == "random_noise_snrs":
        mix_results = mix_random_noises_snrs(clean_files, noise_files, output_filenames, snrs_or_snr)
    elif mode == "random_noise":
        noise_start_noise_indexes = mix_random_noises(clean_files, noise_files, output_filenames, snrs_or_snr)
        for idx, cur in enumerate(noise_start_noise_indexes):
            mix_results[idx][0] = cur[0]
            mix_results[idx][1] = cur[1]
            mix_results[idx][2] = snrs_or_snr
    elif mode == "same":
        noise_starts = mix_noises(clean_files, noise_files, output_filenames, snrs_or_snr)
        for idx, cur in enumerate(noise_starts):
            mix_results[idx][0] = cur[0]
            mix_results[idx][1] = idx
            mix_results[idx][2] = snrs_or_snr
    return mix_results


def make_output_filenames(output_path, clean_files):
    output_filenames = []
    if not os.path.exists(output_path):
        os.makedirs(output_path, exist_ok=True)
    for idx, clean in enumerate(clean_files):
        keyword = os.path.dirname(clean).split("/")[-1]
        output_keyword_path = "{}/{}".format(output_path, keyword)
        if not os.path.exists(output_keyword_path):
            os.makedirs(output_keyword_path, exist_ok=True)
        output_filenames.append("{}/{:06d}.wav".format(output_keyword_path, idx))
    return output_filenames
