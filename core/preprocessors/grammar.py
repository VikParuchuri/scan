import pickle
from scan import settings
from external.tagger.taggers import PerceptronTagger
from core.preprocessors.base import BaseCorrector
import os
from scan.log import logging

log = logging.getLogger(__name__)

class InvalidSequenceException(Exception):
    pass

PICKLE_FILENAME = "grammar.pickle"

class GrammarCorrector(BaseCorrector):
    """
    Adapted from http://honnibal.wordpress.com/2013/09/11/a-good-part-of-speechpos-tagger-in-about-200-lines-of-python/
    """

    lengths = [4]
    min_count = 3

    def __init__(self, load=True):
        super(GrammarCorrector, self).__init__()
        self.data_path = os.path.abspath(os.path.join(settings.DATA_PATH, PICKLE_FILENAME))
        self.model = PerceptronTagger()
        if not load:
            tags, self.good_sequences = self.get_sequences(self.data)
            pickle.dump(self.good_sequences, open(self.data_path, 'wb'))
        else:
            self.good_sequences = pickle.load(open(self.data_path, 'r'))

    def find_bad_sequences(self, sequences):
        bad_sequences = set([])
        for k in sequences:
            count = self.good_sequences.get(k, 0)
            if count < self.min_count:
                bad_sequences.update([k])
        return bad_sequences

    def correct_string(self, string_corpus):
        tags, sequences = self.get_sequences(string_corpus)
        bad_sequences = self.find_bad_sequences(sequences)
        error_ratio = len(bad_sequences) / (float(len(sequences)) + 1)
        new_tags = []
        for t in tags:
            new_tags.append([t[0], t[1], False])

        for l in self.lengths:
            for i in range(l, len(new_tags)):
                nt = new_tags[(i-l):i]
                seq = "_".join([t[1] for t in nt])
                if seq in bad_sequences:
                    for j in range((i-l), i):
                        new_tags[j][2] = True
        for i in range(1, len(new_tags)-1):
            tag = new_tags[i]
            if tag[2] and not new_tags[i-1][2]:
                new_tags[i][0] = "<grammar>" + new_tags[i][0]
            if tag[2] and not new_tags[i+1][2]:
                new_tags[i][0] += "</grammar>"

        words = [nt[0] for nt in new_tags]
        return error_ratio, " ".join(words), new_tags


    def tag(self, string_corpus):
        return self.model.tag(string_corpus)

    def get_pos(self, tags):
        return [t[1] for t in tags]

    def get_sequences(self, string_corpus):
        tags = self.tag(string_corpus)
        pos = self.get_pos(tags)
        sequences = self._get_sequences(pos, self.lengths)
        return tags, sequences

    def _get_sequences(self, pos, lengths):
        sequences = {}
        for l in lengths:
            sequences.update(self._get_sequence(pos, l))
        return sequences

    def _get_sequence(self, pos, length):
        sequences = {}
        if length >= len(pos):
            return sequences

        for i in range(0, len(pos) - length):
            if i % 100000 == 0 and i != 0:
                log.debug("{0}% done with sequence.".format((i/float(len(pos))) * 100))
            val = "_".join(pos[i:i+length])
            if val not in sequences:
                sequences[val] = 0
            sequences[val] += 1
        return sequences