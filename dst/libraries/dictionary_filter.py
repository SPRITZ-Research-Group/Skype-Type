import numpy as np
import os


def dictionary_filter(guesses, wl, howmany=50):

    wl = [x for x in wl if len(x) == len(guesses)]

    def score(word):
        penalty = 0
        for guess, letter in zip(guesses, word):
            if letter in guess:
                penalty += guess.index(letter)
            else:
                penalty += 10
        return penalty

    wls = sorted([(x, score(x)) for x in wl], key=lambda _x: _x[1])

    return wls[:howmany]


def dictionary_interactive(preds, config):
    ans = input("ARE THESE WORDS? [Y/n] ")
    if ans == 'n':
        return
    separators = input("Which are the word separators? (separated with spaces): ").split(" ")

    proposals = [i for i, x in enumerate(preds) if len(set(separators) & set(x)) and
                 min([x.index(c) for c in set(separators) & set(x)]) < config.dict_sep_threshold]
    ans = input("Hint me the correct word segmentation (Suggested spaces in {}): ".format(proposals))
    if ans == '':
        spaces = proposals + [len(preds)]
    else:
        spaces = [int(x) for x in ans.split(" ")] + [len(preds)]
    last_idx = 0

    dictionaries = []
    for r, d, fs in os.walk(config.dict_folder):
        for fn in fs:
            dictionaries.append(os.path.abspath(os.path.join(r, fn)))
    if len(dictionaries) == 0:
        print("No dictionaries available!")
        return
    print("Available dictionaries:")
    for i, d in enumerate(dictionaries):
        print("{} - {}".format(i, d))
    ans = input("Select dictionary number ([0]): ") or 0

    wl = np.loadtxt(dictionaries[int(ans)], dtype=str)
    for space in spaces:
        word_guesses = preds[last_idx:space]
        print("WORD FROM CHARACTER {} to {}".format(last_idx, space))
        print(dictionary_filter(word_guesses, wl, 30))
        print("")
        last_idx = space + 1
