from collections import Counter
from typing import List, Literal, Union, overload

from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords, wordnet
import numpy as np
import pandas as pd
import re
import string

PAT_EMOJI: re.Pattern = re.compile(
    "["
    u"\U0001F600-\U0001F64F"  # emoticons
    u"\U0001F300-\U0001F5FF"  # symbols & pictographs
    u"\U0001F680-\U0001F6FF"  # transport & map symbols
    u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
    u"\U00002702-\U000027B0"
    u"\U000024C2-\U0001F251"
    "]+",
    flags=re.UNICODE
)
PAT_URL: re.Pattern = re.compile(r'https?://\S+|www\.\S+')
STOPWORDS = set(stopwords.words('english'))

lemmatizer = nltk.stem.WordNetLemmatizer()
stemmer = nltk.stem.PorterStemmer()
wordnet_map = {
    'N': wordnet.NOUN, 'V': wordnet.VERB, 'J': wordnet.ADJ, 'R': wordnet.ADV
}


@overload
def standardize_formatting(
    df: pd.Series,
    keep_urls: bool = False,
    keep_emoji: bool = False
) -> pd.Series:
    ...


@overload
def standardize_formatting(
    df: pd.DataFrame,
    keep_urls: bool = False,
    keep_emoji: bool = False
) -> pd.DataFrame:
    ...


def standardize_formatting(
    df: Union[pd.DataFrame, pd.Series],
    keep_urls: bool = False,
    keep_emoji: bool = False,
    stemming: Literal['stem', 'lemmatize'] = None
) -> Union[pd.DataFrame, pd.Series]:
    """Function for easily standardizing all text in a DataFrame or Series.

    When run, this function will:
        1. remove all punctuation from the text
        2. send all text to lowercase
        3. remove emoji (if keep_emoji=False)
        4. remove urls (if keep_urls=False)

    Parameters
    ----------
    df : pd.DataFrame or pd.Series
        The DataFrame or series to format. If this is a DataFrame, all columns
        passed in will have formatting applied.
    keep_urls : bool, optional
        Keeps URLs present in all text if True, by default False
    keep_emoji : bool, optional
        Keeps emoji present in all text if True, by default False
    stemming : 'stem' or 'lemmatize'
        If not None, will either stem or lemmatize words depending in on
        the passed in string identifier ('stem' for stemming and 'lemmatize'
        for lemmatizing). By default None.

    Returns
    -------
    pd.DataFrame or pd.Series
        Returns a formatted version of the passed in data.
    """
    # iterate columns if it's a DataFrame
    if isinstance(df, pd.DataFrame):
        for col in df.columns:
            df[col] = df[col].apply(lambda t: remove_punctuation(t)).str.lower()
            df[col] = df[col].str.replace(r'\[.*?\]', '')
            if not keep_emoji:
                df[col] = df[col].apply(lambda t: remove_emoji(t))
            if not keep_urls:
                df[col] = df[col].apply(lambda t: remove_urls(t))
            if stemming:
                df[col] = df[col].apply(lambda t: stem_words(t, stemming))
    # No columns for a series, so just apply to series directly
    else:
        df = df.apply(lambda t: remove_punctuation(t)).str.lower()
        df = df.str.replace(r'\[.*?\]|\n|\w+\d+\w+', '')
        if not keep_emoji:
            df = df.apply(lambda t: remove_emoji(t))
        if not keep_urls:
            df = df.apply(lambda t: remove_urls(t))

    return df


def remove_words(
    df: Union[pd.DataFrame, pd.Series],
    stopwords: bool = False,
    freqwords: int = 0,
    rarewords: int = 0
) -> Union[pd.DataFrame, pd.Series]:
    """Removes sets of words from the passed in text.

    Parameters
    ----------
    df : pd.DataFrame or pd.Series
        The DataFrame or Series to remove words from. If this is a DataFrame,
        all columns passed in will have the indicated words removed.
    stopwords : bool, optional
        Removes stopwords from the text when True, by default False
    freqwords : int, optional
        The number of most frequent words to remove, by default 0
    rarewords : int, optional
        The number of least frequent words to remove, by default 0

    Returns
    -------
    pd.DataFrame or pd.Series
        Returns the same data type as passed in, but with the indicated words
        removed.
    """
    if isinstance(df, pd.DataFrame):
        for col in df.columns:
            counter = Counter()
            if freqwords > 0 or stopwords > 0:
                for text in df[col].values:
                    for word in text.split():
                        counter[word] += 1

            if stopwords:
                df[col] = df[col].apply(lambda t: remove_wordlist(t, STOPWORDS))
            if freqwords > 0:
                top_words = set(
                    [w for (w, _) in counter.most_common(freqwords)]
                )
                df[col] = df[col].apply(lambda t: remove_wordlist(t, top_words))
            if rarewords > 0:
                btm_words = set(
                    [w for (w, _) in counter.most_common()[:-rarewords - 1:-1]]
                )
                df[col] = df[col].apply(lambda t: remove_wordlist(t, btm_words))

    else:
        counter = Counter()
        if freqwords > 0 or stopwords > 0:
            for text in df.values:
                for word in text.split():
                    counter[word] += 1

        if stopwords:
            df = df.apply(lambda t: remove_wordlist(t, STOPWORDS))
        if freqwords > 0:
            top_words = set([w for (w, _) in counter.most_common(freqwords)])
            df = df.apply(lambda t: remove_wordlist(t, top_words))
        if rarewords > 0:
            btm_words = set(
                [w for (w, _) in counter.most_common()[:-rarewords - 1:-1]]
            )
            df = df.apply(lambda t: remove_wordlist(t, btm_words))

    return df


def stem_words(text: str, mode: Literal['stem', 'lemmatize']) -> str:
    if mode == 'stem':
        return " ".join([stemmer.stem(w) for w in text.split()])
    else:
        tagged = nltk.pos_tag(text.split())
        return " ".join(
            [
                lemmatizer.lemmatize(w, wordnet_map.get(pos[0], wordnet.NOUN))
                for w,
                pos in tagged
            ]
        )


def remove_emoji(text: str) -> str:
    """Removes emoji from a body of text."""
    return PAT_EMOJI.sub(r'', text)


def remove_html(text: str) -> str:
    """Removes all HTML tags from a body of text."""
    return BeautifulSoup(text, 'lxml').text


def remove_punctuation(text: str) -> str:
    """Removes all punctuation marks from a body of text."""
    return text.translate(str.maketrans('', '', string.punctuation))


def remove_urls(text: str) -> str:
    """Removes URLs from a body of text."""
    return PAT_URL.sub(r'', text)


def remove_wordlist(text: str, wordlist: List[str]) -> str:
    """Removes words from the passed in wordlist from a body of text."""
    return " ".join([w for w in str(text).split() if w not in wordlist])


def tokenization(text: str) -> List[str]:
    return [word for word in nltk.word_tokenize(text) if word.isalpha()]
