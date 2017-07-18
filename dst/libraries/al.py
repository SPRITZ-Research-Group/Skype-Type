import os
import math
import warnings
import numpy as np
import scipy.io.wavfile as wav


def is_sequence(arg):
    return (not hasattr(arg, "strip") and
            hasattr(arg, "__getitem__") or
            hasattr(arg, "__iter__")) and not isinstance(arg, np.float64)


def split_channels(data):
    return data[:, 0].astype(float), data[:, 1].astype(float)


def __read_wav(filename):
    meta, data = wav.read(filename)
    data = np.array(data)
    try:
        ch1, ch2 = split_channels(data)
    except IndexError:
        warnings.warn('Given audio is mono')
        ch1, ch2 = data, np.zeros(len(data))
    if filename.find('_') != -1:
        letter = filename.split('_')[-2]
    else:
        letter = ''
    return (ch1, ch2), normalize(ch1 + ch2), letter


def __read_text(filename):
    return [], np.loadtxt(filename), os.path.splitext(filename)[0][-1]


def reader(filename):
    if os.path.splitext(filename)[1] == '.wav':
        return __read_wav(filename)
    else:
        return __read_text(filename)


def load(path):
    if os.path.isdir(path):
        stereo = {}
        mono = {}
        for filename in os.listdir(path):
            stereo_data, mono_data, letter = reader(path + filename)
            stereo[letter], mono[letter] = stereo_data, mono_data
        return stereo, mono
    else:
        stereo, mono, letter = reader(path)
        return stereo, mono


def rms(series):
    return math.sqrt(sum(series ** 2) / series.size)


def normalize(series):
    return series / rms(series)
