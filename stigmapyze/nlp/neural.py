from typing import Any, Dict, Final, List, Tuple
import os

from keras.callbacks import EarlyStopping
from keras import layers
from keras.layers.core import Dense, Activation, Dropout
from keras.layers.embeddings import Embedding
from keras.layers.normalization import BatchNormalization
from keras.layers.recurrent import LSTM, SimpleRNN
from keras.models import Sequential
from keras.preprocessing import sequence, text
import numpy as np
import tensorflow as tf
import tqdm

GLOVE_TXT: Final[str] = os.path.expandvars(
    '${XDG_DATA_HOME}/michael/data-science/glove.840B.300d.txt'
)


def sequence_data(X_train, X_test) -> Tuple[np.ndarray, np.ndarray, dict]:
    tokenizer = text.Tokenizer(num_words=None)
    tokenizer.fit_on_texts(list(X_train) + list(X_test))
    X_train_seq = sequence.pad_sequences(
        tokenizer.texts_to_sequences(X_train), maxlen=1500
    )
    X_test_seq = sequence.pad_sequences(
        tokenizer.texts_to_sequences(X_test), maxlen=1500
    )
    return X_train_seq, X_test_seq, tokenizer.word_index


def load_glove_index(word_index: Dict[Any, int]):
    eindex: Dict[str, List[float]] = {}
    ematrix: np.ndarray = np.zeros((len(word_index) + 1, 300))
    with open(GLOVE_TXT, 'r', encoding='utf-8') as glove:
        for line in tqdm(glove):
            values = line.split(' ')
            word, coef = values[0], np.asarray([float(v) for v in values[1:]])
            eindex[word] = coef

    for word, idx in tqdm(word_index.items()):
        coef = eindex.get(word)
        if coef:
            ematrix[idx] = coef

    return eindex, ematrix


def rnn_simple(d_inp, d_out, inp_len, rnn_units) -> Sequential:
    model = Sequential(
        [
            Embedding(d_inp, d_out, input_length=inp_len),
            SimpleRNN(rnn_units),
            Dense(10, activation='softmax'),
        ]
    )
    model.compile(
        optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy']
    )
    return model


def lstm_simple(d_inp, d_out, inp_len, ematrix, lstm_units) -> Sequential:
    model = Sequential(
        [
            Embedding(
                d_inp,
                d_out,
                input_length=inp_len,
                weights=[ematrix],
                trainable=False
            ),
            LSTM(100, dropout=.3, recurrent_dropout=.3),
            Dense(10, activation='softmax'),
        ]
    )
    model.compile(
        optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy']
    )
    return model
