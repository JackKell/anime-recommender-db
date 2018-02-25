import re
import string

import numpy
import pandas
from nltk.corpus import stopwords


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


def intRound(x, base):
    return int(base * round(float(x)/base))

# following function credited to https://buhrmann.github.io/tfidf-analysis.html
def top_tfidf_feats(row, features, top_n=25):
    ''' Get top n tfidf values in row and return them with their corresponding feature names.'''
    topn_ids = numpy.argsort(row)[::-1][:top_n]
    top_feats = [(features[i], row[i]) for i in topn_ids]
    df = pandas.DataFrame(top_feats)
    df.columns = ['feature', 'tfidf']
    return df


def top_feats_in_doc(Xtr, features, row_id, top_n=25):
    ''' Top tfidf features in specific document (matrix row) '''
    row = numpy.squeeze(Xtr[row_id].toarray())
    return top_tfidf_feats(row, features, top_n)


def top_mean_feats(Xtr, features, grp_ids=None, min_tfidf=0.1, top_n=25):
    ''' Return the top n features that on average are most important amongst documents in rows
        indentified by indices in grp_ids. '''
    if grp_ids:
        D = Xtr[grp_ids].toarray()
    else:
        D = Xtr.toarray()

    D[D < min_tfidf] = 0
    tfidf_means = numpy.mean(D, axis=0)
    return top_tfidf_feats(tfidf_means, features, top_n)
