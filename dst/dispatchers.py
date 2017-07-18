import numpy as np
from dst.libraries import al
import warnings

warnings.filterwarnings("ignore")


def offline(in_queue, out_queue, display_queue, config):
    """

    :param in_queue: Queue to receive audio file
    :type in_queue: multiprocessing.Queue
    :param out_queue: Queue where to put extracted keypress samples
    :type out_queue: multiprocessing.Queue
    :param display_queue: Queue where to put visual information to be displayed
    :type display_queue: multiprocessing.Queue
    :param config: a Config object
    :type config: Config
    :return: None
    :rtype:
    """
    for data in iter(in_queue.get, None):
        rem = len(data) % 441
        data = np.array(data[:len(data) - rem])
        minimum_interval = config.dispatcher_min_interval
        sample_length = (44100 * config.dispatcher_window_size) / 1000

        persistence = config.dispatcher_persistence

        peaks = []
        for x in range(0, len(data) - 440):
            peaks.append(np.sum(np.absolute(np.fft.fft(data[x:x + 440]))))

        peaks = np.array(peaks)
        tau = np.percentile(peaks, config.dispatcher_threshold)

        x = 0
        events = []
        step = config.dispatcher_step_size
        past_x = - minimum_interval - step
        idx = 0
        while x < peaks.size:
            if peaks[x] >= tau:
                if x - past_x >= minimum_interval:
                    # It is a keypress event (maybe)
                    keypress = al.normalize(data[x:x + sample_length])
                    past_x = x
                    # Pass it immediately to workers
                    out_queue.put([idx, keypress])
                    idx += 1
                    # Display event point
                    # display_queue.put(x)
                    events.append(keypress)
                x = past_x + minimum_interval
            else:
                x += step

        display_queue.put(len(events))
        # If persistence, save stuff to path
        # TODO implement it
        if persistence:
            pass

    # Send termination flag to workers
    for _x in xrange(config.workers):
        out_queue.put((-1, None))
