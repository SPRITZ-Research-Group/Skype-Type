#! /usr/bin/python3

import argparse
import importlib
import os
from multiprocessing import Process
from multiprocessing import Queue
import itertools
import numpy as np
from sklearn.externals import joblib
from sklearn.feature_selection import RFECV
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler

from config import *
from dst.dispatchers import offline
from dst.listeners import wavfile
import dst.miners

if __name__ == "__main__":

    # Argument parsing
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='Generate a S&T attack model using specified training data',
        epilog='''\

    This is a convenience program to train a ML model on a set of ground truth data, and generate the respective pipeline,
    to be used in S&T.
    
    Training data can be passed as any list of files and folders.
    Only requirement is that, for each WAV file containing training material, a corresponding ground truth file with 
    identical name but .txt extension is present anywhere in the given files and folders.
    This means that if you call
        %(prog)s training.wav myfolder
    Then, a training.txt file, containing ground truth for training.wav, has to exist in folder "myfolder", or any of
    its subdirectories.
    
    If using a custom classifier, it needs to be passed as CLASS_NAME PACKAGE_NAME as argument.
    For example, to use sklearn.ensemble.RandomForestClassifier, you should pass
        %(prog)s --classifier RandomForestClassifier sklearn.linear_model
    as options to this program.
        '''
    )
    parser.add_argument('--version', '-v', action='version', version=CONFIG.VERSION)
    parser.add_argument('training_data', nargs='+', type=str, help='List of files and folders containing training data')
    parser.add_argument('output_file', type=str, help='Path of the resulting trained model')
    parser.add_argument('--features', '-f', default='MFCC', help='Feature extraction class')
    parser.add_argument('--no_feature_extraction', action='store_true', help='Whether to perform feature extraction')
    parser.add_argument('--no_scaling', action='store_true', help='Whether to scale features between [0,1] (suggested)')
    parser.add_argument('--no_feature_selection', action='store_true', help='Whether to perform Recursive Feature Elimination before training (slow)')
    parser.add_argument('--folds', type=int, default=5, help='How many folds to use for cross-validation')
    parser.add_argument('--n_threads', '-n', type=int, default=4, help='Parallelism')
    parser.add_argument('--classifier', '-c', nargs=2, default=['LogisticRegression', 'sklearn.linear_model'], help='Class name and package name of classifier')

    args = parser.parse_args()

    # Training files
    files_to_mine = {}
    mined_files = {}
    wav_files = []
    label_files = []
    press_files = []


    def add_file(fl):
        ext = os.path.splitext(fl)[1]
        if ext == '.wav':
            wav_files.append(fl)
        elif ext == '.press':
            press_files.append(fl)
        elif ext == '.txt':
            label_files.append(fl)

    # Read training files from specified location
    for f_name in args.training_data:
        f = os.path.abspath(f_name)
        if os.path.isfile(f):
            add_file(f)
        elif os.path.isdir(f):
            for r, d, fs in os.walk(f):
                for fn in fs:
                    f1 = os.path.abspath(os.path.join(r, fn))
                    add_file(f1)

    # Every wavfile and pressfile needs a corresponding label file (same name, any extension)
    # Otherwise exit and report the error
    wavfiles_map = {}
    for f in wav_files:
        basename = os.path.splitext(os.path.basename(f))[0]
        if os.path.splitext(f)[0] + '.press' not in press_files:
            wavfiles_map[f] = None
            for l_f in label_files:
                if os.path.splitext(os.path.basename(l_f))[0] == basename:
                    wavfiles_map[f] = l_f
    pressfiles_map = {}
    for f in press_files:
        basename = os.path.splitext(os.path.basename(f))[0]
        pressfiles_map[f] = None
        for l_f in label_files:
            if os.path.splitext(os.path.basename(l_f))[0] == basename:
                pressfiles_map[f] = l_f

    mismatches = [x for x, y in wavfiles_map.items() if y is None] + \
                 [x for x, y in pressfiles_map.items() if y is None]
    if len(mismatches) != 0:
        print("Can't find labels for some wav files / press files!")
        print("Offending files:")
        for f in mismatches:
            print(f)
        exit()

    # Divide each file in samples corresponding to keys
    # For each worker get features and labels and put them in final arrays X and y
    # They start as lists (we don't know their lengths yet)
    print("Found {} files already mined".format(len(press_files)))
    print("Found {} files to mine".format(len(wav_files) - len(press_files)))
    f_X, f_y = [], []
    error_queue = []
    # We divide files in groups of n_thread size
    # We iterate over groups, and spawn a miner process for each file
    # We then wait for them to implicitly join when reporting results, and collect mined data
    for grp_idx, grp_it in itertools.groupby(enumerate(wavfiles_map.items()), lambda _fg: int(_fg[0] / args.n_threads)):
        events_queue = []
        for i, (wav_file, label_file) in grp_it:
            print("Processing file #{}".format(i + 1))
            lq = Queue()
            p = Process(target=wavfile, args=(wav_file, lq, CONFIG))
            p.daemon = True
            p.start()

            # Create offline dispatcher
            # Dispatch file
            oq, dq = Queue(), Queue()
            p = Process(target=offline, args=(lq, oq, dq, CONFIG))
            p.daemon = True
            p.start()

            y = np.loadtxt(label_file, dtype=str)
            events_queue.append((wav_file, y, oq, dq))

        for wav_file, y, oq, dq in events_queue:
            n_res = dq.get()
            if not len(y.shape):
                # Happens if a ground truth file has a single row
                # This is probably not what the user means, but we can't be sure
                # So we just assumes he intended it
                y = y.reshape(1)
            if n_res != len(y):
                # More mined events than ground truth values
                error_queue.append((wav_file, n_res, len(y)))
            else:
                _x = []
                # Collect results until the number of letters we know is in the file
                while len(_x) < len(y):
                    _x.append(oq.get())
                X = [[] for _ in range(len(_x))]
                for idx, sample in _x:
                    X[idx] = sample
                np.savetxt(os.path.splitext(wav_file)[0] + '.press', X)
                f_X.extend(X)
                f_y.extend(y)

    if len(error_queue) != 0:
        print("Error in reading some files - wrong n. of keypresses found:")
        for f, found, expected in error_queue:
            print("{} - found {}, expected {}".format(f, found, expected))
        exit()

    # .press files already present only need to be loaded from disk and appended to the matrix
    for i, (press_file, label_file) in enumerate(pressfiles_map.items()):
        f_X.extend(np.loadtxt(press_file))
        f_y.extend(np.loadtxt(label_file, dtype=str))
    f_X, f_y = np.array(f_X), np.array(f_y)

    # Load pipeline steps
    # 1 - Feature extraction
    pipeline = []
    if not args.no_feature_extraction:
        pipeline.append((args.features, getattr(dst.miners, args.features)()))
    if not args.no_scaling:
        pipeline.append(('Scaler', MinMaxScaler()))
    # 2 - Feature selector and classifier
    classifier = getattr(importlib.import_module(args.classifier[1]), args.classifier[0])()
    if not args.no_feature_selection:
        pipeline.append(('Feature Selection',
                         RFECV(classifier, step=f_X.shape[1] / 10, cv=args.folds, verbose=0)))
    pipeline.append(('Classifier', classifier))
    clf = Pipeline(pipeline)

    print("Learning...")
    # Fit and save fitted model to file. Output stats about estimated accuracy
    clf.fit(f_X, f_y)
    print("Learning task completed!")
    print("Writing model to disk")
    joblib.dump(clf, args.output_file)
    print("Estimating accuracy...")
    print(np.mean(cross_val_score(clf, f_X, f_y, cv=args.folds+1)))
