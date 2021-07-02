from nltk import word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer

STOPWORDS = set(stopwords.words('english'))


def sentence_vec_normed(text: str):
    words = [
        word for word in word_tokenize(str(text).lower().decode('utf-8'))
        if not word in STOPWORDS and word.isalpha()
    ]

    embedded = []
    for word in words:
        continue
