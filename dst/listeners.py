from dst.libraries import al
import warnings

warnings.filterwarnings("ignore")


def wavfile(in_file, out_queue, config):
    _, mono = al.load(in_file)
    out_queue.put(mono)
    out_queue.put(None)


def input_recording():
    pass


def input_interactive():
    pass
