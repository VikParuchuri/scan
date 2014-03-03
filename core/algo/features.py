from core.preprocessors.grammar import GrammarCorrector
from core.preprocessors.spelling import SpellCorrector
from stemming.porter2 import stem
from core.algo.vectorizer import Vectorizer
import re
import numpy as np

class FeatureGenerator(object):
    def __init__(self, normal_vectorizer=None, clean_vectorizer=None):
        self.mf_generator = MetaFeatureGenerator()
        self.fit_complete = False
        if normal_vectorizer and clean_vectorizer:
            self.fit_complete = True

        if normal_vectorizer:
            self.normal_vectorizer = normal_vectorizer
        else:
            self.normal_vectorizer = Vectorizer()

        if clean_vectorizer:
            self.clean_vectorizer = clean_vectorizer
        else:
            self.clean_vectorizer = Vectorizer()

    def fit(self, input_text, input_scores):
        self.normal_vectorizer.fit(input_text, input_scores)
        clean_text = [self.mf_generator.generate_clean_stem_text(t) for t in input_text]
        self.clean_vectorizer.fit(clean_text, input_scores)

    def get_features(self, text):
        vec_feats = self.generate_vectorizer_features(text)
        vec_keys = self.normal_vectorizer.vocab + self.clean_vectorizer.vocab

        meta_feats = self.generate_meta_features(text)
        meta_keys = meta_feats.keys()
        meta_keys.sort()
        meta_feat_arr = np.matrix([meta_feats[k] for k in meta_keys])

        self.colnames = vec_keys + meta_keys

        return np.hstack([vec_feats, meta_feat_arr])

    def generate_meta_features(self, text):
        feats = self.mf_generator.generate_meta_features(text)
        return feats

    def generate_vectorizer_features(self, text):
        clean_text = self.mf_generator.generate_clean_stem_text(text)
        feats = self.normal_vectorizer.get_features([text])
        clean_feats = self.clean_vectorizer.get_features([clean_text])
        return np.hstack([feats, clean_feats])

class MetaFeatureGenerator(object):
    speech_parts = dict(
        nouns=["NN", "NNP", "NNPS", "NNS"],
        verbs=["VB", "VBD", "VBG", "VBN", "VBP", "VBZ"],
        adjectives=["JJ", "JJR", "JJS"],
        adverbs=["RB", "RBR", "RBS"]
    )

    def __init__(self):
        self.grammar = GrammarCorrector()
        self.spelling = SpellCorrector()
        self.stem = stem

    def generate_grammar_features(self, raw_grammar):
        grammar_counts = {}
        for k in self.speech_parts:
            grammar_counts[k] = 0

        for t in raw_grammar:
            for k in self.speech_parts:
                if t[1] in self.speech_parts[k]:
                    grammar_counts[k] += 1
        for k in grammar_counts:
            grammar_counts[k] /= len(raw_grammar)
        return grammar_counts

    def clean_spell_corrected_tags(self, spelling_markup):
        return re.sub("<[^>]+>", '', spelling_markup)

    def generate_text_features(self, text):
        feats = {}
        feats['length'] = len(text)
        feats['word_length'] = len(text.split())
        feats['sentence_length'] = len(text.split("."))
        feats['chars_per_sentence'] = feats['length'] / (feats['sentence_length'] + 1)
        feats['words_per_sentence'] = feats['word_length'] / (feats['sentence_length'] + 1)
        feats['chars_per_word'] = feats['length'] / (feats['word_length'] + 1)
        return feats

    def generate_clean_stem_text(self, text):
        spelling_errors, spelling_markup, raw_spelling = self.spelling.correct_string(text)
        clean_text = self.clean_spell_corrected_tags(spelling_markup)
        clean_text = re.sub("[^A-Za-z0-9 \.,\'\":;]", " ", clean_text.lower())
        clean_text = re.sub("\s+", " ", clean_text)
        clean_text = ' '.join([self.stem(t) for t in clean_text.split(' ')])
        return clean_text

    def generate_meta_features(self, text):
        features = {}
        grammar_errors, grammar_markup, raw_grammar = self.grammar.correct_string(text)
        features['grammar_errors'] = grammar_errors
        grammar_feats = self.generate_grammar_features(raw_grammar)
        features.update(grammar_feats)

        spelling_errors, spelling_markup, raw_spelling = self.spelling.correct_string(text)
        features['spelling_errors'] = spelling_errors

        text_feats = self.generate_text_features(text)
        features.update(text_feats)

        return features