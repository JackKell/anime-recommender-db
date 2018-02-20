import math
import string

import nltk
from nltk.corpus import stopwords
import re
from textblob import TextBlob


# code credit for tf, n_containing, idf, and tfidf to https://stevenloria.com/tf-idf/
def tf(word, blob):
    return blob.words.count(word) / len(blob.words)


def n_containing(word, bloblist):
    return sum(1 for blob in bloblist if word in blob.words)


def idf(word, bloblist):
    return math.log(len(bloblist) / (1 + n_containing(word, bloblist)))


def tfidf(word, blob, bloblist):
    return tf(word, blob) * idf(word, bloblist)


def cleanText(text):
    cleanedText = text
    # Remove line endings
    cleanedText = cleanedText.replace("\r", "").replace("\n", " ")
    # To lowercase
    cleanedText = cleanedText.lower()
    # Remove Punctuation
    cleanedText = removePunctuation(cleanedText)
    return cleanedText


def removeStopWords(words):
    stops = set(stopwords.words("english"))
    return [word for word in words if word not in stops]


def removePunctuation(text):
    return re.sub("[" + string.punctuation + "]", "", text)
