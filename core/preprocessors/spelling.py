import pickle
import re
import collections
from scan import settings
import os
from core.preprocessors.base import BaseCorrector

def one():
    return 1

class SpellCorrector(BaseCorrector):
    """
    Slightly adapted from Peter Norvig's spell corrector:  http://norvig.com/spell-correct.html
    """
    alphabet = 'abcdefghijklmnopqrstuvwxyz'

    def __init__(self):
        super(SpellCorrector, self).__init__()
        self.data_path = os.path.abspath(os.path.join(settings.DATA_PATH, "big.txt"))
        self.nwords = self.train(self.words(self.data))

    def correct_string(self, string_corpus):
        words = string_corpus.split(' ')
        mistakes = 0
        new_words = []
        for w in words:
            real_word = re.sub(r'[^a-zA-Z]', '', w)
            if len(real_word) == 0:
                new_words.append(w)
                continue

            corrected_word = self.correct(real_word)

            if real_word[0].upper() == real_word[0]:
                corrected_word = corrected_word[0].upper() + corrected_word[1:]

            new_word = w
            if corrected_word.lower() != real_word.lower():
                mistakes += 1
                new_word = "<spelling data-old='{0}'>".format(w) + w.replace(real_word, corrected_word) + "</spelling>"
            new_words.append(new_word)
        return mistakes / float(len(words) + 1), ' '.join(new_words), new_words

    def train(self, features):
        model = collections.defaultdict(one)
        for f in features:
            model[f] += 1
        return model

    def edits1(self, word):
        splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        deletes = [a + b[1:] for a, b in splits if b]
        transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
        replaces = [a + c + b[1:] for a, b in splits for c in self.alphabet if b]
        inserts = [a + c + b for a, b in splits for c in self.alphabet]
        return set(deletes + transposes + replaces + inserts)

    def known_edits2(self, word):
        return set(e2 for e1 in self.edits1(word) for e2 in self.edits1(e1) if e2 in self.nwords)

    def known(self, words):
        return set(w for w in words if w in self.nwords)

    def correct(self, word):
        w = word.lower()
        candidates = self.known([w]) or self.known(self.edits1(w)) or self.known_edits2(w) or [w]
        return max(candidates, key=self.nwords.get)