from typing import Tuple
from matplotlib.axes import Axes
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import CountVectorizer


def get_ngrams(text, n: int, amount: int):
    counter = CountVectorizer(ngram_range=(n, n)).fit(text)
    bow_sum = counter.transform(text).sum(axis=0)
    freqs = [(w, bow_sum[0, i]) for w, i in counter.vocabulary_.items()]
    return sorted(freqs, key=lambda t: t[1], reverse=True)[:amount]


def plot_ngrams(text, n: int, amount: int) -> Tuple[Figure, Axes, list]:
    fig, ax = plt.subplots(figsize=(16, 10))
    ngrams = get_ngrams(text, 1, amount)
    ax = sns.barplot(
        x=list(map(lambda t: t[0], ngrams)),
        y=list(map(lambda t: t[1], ngrams))
    )
    ax.set_title(f'NGrams (N={n}), by frequency')
    ax.set_xlabel('Frequency (count)')
    ax.set_ylabel('ngrams')
    return fig, ax, ngrams
