# Don't Skype & Type!

S&T is a novel, powerful, and open-source research tool for keyboard acoustic eavesdropping.

It allows users to perform *keyboard acoustic eavesdropping* attacks: training a Machine Learning model on the different
noise of each key of someone's keyboard, and then use this model to understand what he's typing from keystroke noise
alone.

Don't Skype & Type! is a research project from [SPRITZ Group](http://spritz.math.unipd.it) (University of Padua, IT), and [SPROUT](http://sprout.ics.uci.edu) (UC Irvine, USA).
For further information see our project webpage: http://spritz.math.unipd.it/projects/dst/

If you use our tool in your own research, please cite our paper:

    Compagno, A., Conti, M., Lain, D., & Tsudik, G. (2017, April).
    Don't Skype & Type!: Acoustic Eavesdropping in Voice-Over-IP.
    In Proceedings of the 2017 ACM on Asia Conference on Computer and Communications Security (pp. 703-715). ACM.


## Introduction

S&T is built around the concept of *operator chains*, concatenated basic blocks that provide functionalities.
This modular design allows for customization of every operation.

A chain is composed of four main blocks: a *Listener*, a *Dispatcher*, a *Model*, and an *Output*.

On each block, a different function can be loaded (provided that it can work with its previous and next block), as long
as the correct interface is implemented. Each function has its own *subprocess*, and communicates using
`multiprocessing.Queue` objects.

*Listener* functions are responsible of loading sound and passing it to a *Dispatcher*, that extracts keypress sounds
from the audio file or stream, and passes it to a trained *Model* that performs classification. Finally, results are
passed to *Output* operators, that show classification results.

## Usage

First, you need to create a `sklearn.Pipeline` containing a classifier, plus any other data transformation
you want.

A convenient way to create it is to use `generate_model`, passing training data to it:

> generate_model.py training_files_and_folders output_model [...]

Which will take as training data all the files passed as arguments, and all the files contained in folders that are
passed as arguments. The trained model will be saved in the specified location.
Please note: acoustic training data needs to be .wav (Microsoft), 32bit float PCM.
For each .wav file passed as training, a corresponding .txt file with identical name needs to contain its ground truth,
**one target/character per line**. NOTE: spaces are not allowed as characters in ground truth -- please replace them with another
character.

When launching S&T, operator chains can be specified manually through CLI parameters, such as:

> main.py --listener wavfile --dispatcher offline ...

or convenient *opmodes*, that automatically load blocks, can be used:

> main.py --opmode from_file

More information about each block, possible options, and usage can be found on the `User Guide`_.

## Examples

Generate a model from training data in file1.wav, file1.txt, and all files in folder1 and folder2, and save it in folder3/model(note: specifying individual filenames will force the program to reprocess the specified files each time and not take advantage of the generated press files it is better to specify a containing folder of the wav and txt files):

> generate_model.py file1.wav file1.txt folder1 folder2 folder3/model

Run S&T on target.wav, using the pipeline saved in folder3/model:

> main.py --opmode from_file --target target.wav --pipeline folder3/model

Run S&T on target.wav, using the pipeline saved in folder3/model, manually specifying a listener and dispatcher block:

> main.py --listener wavfile --dispatcher offline --target target.wav --pipeline folder3/model

## Requirements

Eventually, this software will have a proper installer and dependency management.
For now, you'll need to install dependencies manually:

    sklearn
    numpy
    python_speech_features
    
Additionally, if you want to fully leverage S&T against words in a known language, please provide your own dictionaries
in the /dictionaries folder.

## TODO

- Finish proper documentation and generate it
- Upload unit tests
