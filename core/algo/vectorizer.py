from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
from scipy.stats import fisher_exact
from scan import settings

class Vectorizer(object):
    max_features = settings.MAX_FEATURES / 2

    def __init__(self):
        self.fit_done = False

    def fit(self, input_text, input_scores):
        self.initial_vectorizer = CountVectorizer(ngram_range=(1, 2), min_df = 3 / len(input_text), max_df=.4)
        self.initial_vectorizer.fit(input_text)
        self.vocab = self.get_vocab(self.initial_vectorizer, input_text, input_scores)
        self.vectorizer = CountVectorizer(ngram_range=(1, 2), vocabulary=self.vocab)
        self.fit_done = True
        self.input_text = input_text

    def get_vocab(self, vectorizer, input_text, input_scores):
        train_mat = vectorizer.transform(input_text)
        input_score_med = np.median(input_scores)
        new_scores = [0 if i <= input_score_med else 1 for i in input_scores]

        pvalues = []
        for i in range(0, train_mat.shape[1]):
            lcol = np.asarray(train_mat.getcol(i).todense().transpose())[0]
            good_lcol = lcol[[n for n in range(0, len(new_scores)) if new_scores[n] == 1]]
            bad_lcol = lcol[[n for n in range(0, len(new_scores)) if new_scores[n] == 0]]
            good_lcol_present = len(good_lcol[good_lcol > 0])
            good_lcol_missing = len(good_lcol[good_lcol == 0])
            bad_lcol_present = len(bad_lcol[bad_lcol > 0])
            bad_lcol_missing = len(bad_lcol[bad_lcol == 0])
            oddsratio, pval = fisher_exact([[good_lcol_present, bad_lcol_present], [good_lcol_missing, bad_lcol_missing]])
            pvalues.append(pval)

        col_inds = range(0, train_mat.shape[1])
        p_frame = np.array([col_inds, pvalues]).transpose()
        p_frame = p_frame[p_frame[:, 1].argsort()]

        rows = p_frame.shape[0]
        selection = self.max_features
        if rows < selection:
            selection = rows

        getVar = lambda searchList, ind: [searchList[int(i)] for i in ind]
        vocab = getVar(vectorizer.get_feature_names(), p_frame[:, 0][-selection:])
        return vocab

    def get_features(self, text):
        if not self.fit_done:
            raise Exception("Vectorizer has not been created.")
        return self.vectorizer.transform(text).todense()