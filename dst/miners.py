import python_speech_features as sf
from sklearn.base import BaseEstimator, ClassifierMixin
import numpy as np


class BaseMiner(BaseEstimator, ClassifierMixin):
    def fit(self, X, y):
        return self


class MFCC(BaseMiner):
    @staticmethod
    def transform(X):
        return np.array([sf.mfcc(sample, 44100, 0.01, 0.0025, 32, 32, preemph=0, highfreq=12000, ceplifter=0,
                       appendEnergy=False).flatten() for sample in X])
