from core.tests.base import ScanTest
from scan.log import logging
from core.tests.base import db
from mock import patch
from core.algo.scorer import Scorer
import os
import json
from scan import test_settings as settings
import random

log = logging.getLogger(__name__)

class DataLoader(object):
    def __init__(self, pathname):
        self.pathname = pathname

    def load_text_files(self, pathname):
        filenames = os.listdir(pathname)
        text = []
        for filename in filenames:
            data = open(os.path.join(pathname, filename)).read()
            text.append(data[:settings.CHARACTER_LIMIT])
        return text

    def load_json_file(self, filename):
        datafile = open(os.path.join(filename))
        data = json.load(datafile)
        return data

    def load_data(self):
        """
        Override when inheriting
        """
        raise NotImplementedError()

class PolarityLoader(DataLoader):

    def load_data(self):
        filenames = os.listdir(self.pathname)
        directories = [os.path.abspath(os.path.join(self.pathname, f)) for f in filenames if not os.path.isfile(os.path.join(self.pathname,f)) and f in ["neg", "pos"]]

        #Sort so neg is first
        directories.sort()
        #We need to have both a postive and a negative folder to classify
        if len(directories)!=2:
            raise Exception("Need a pos and a neg directory in {0}".format(self.pathname))

        neg = self.load_text_files(directories[0])
        pos = self.load_text_files(directories[1])

        scores = [0 for i in range(0, len(neg))] + [1 for i in range(0, len(pos))]
        text = neg + pos

        return scores, text

class GenericTest(object):
    loader = DataLoader
    data_path = ""
    expected_mae_max = 0

    def load_data(self):
        data_loader = self.loader(os.path.join(settings.TEST_DATA_PATH, self.data_path))
        scores, text = data_loader.load_data()
        return scores, text

    def generic_setup(self, scores, text):
        #Shuffle to mix up the classes, set seed to make it repeatable
        random.seed(1)
        shuffled_scores = []
        shuffled_text = []
        indices = [i for i in range(0, len(scores))]
        random.shuffle(indices)
        for i in indices:
            shuffled_scores.append(scores[i])
            shuffled_text.append(text[i])

        self.text = shuffled_text[:settings.TRAINING_LIMIT]
        self.scores = shuffled_scores[:settings.TRAINING_LIMIT]

    def model_creation_and_grading(self):
        score_subset = self.scores[:settings.QUICK_TEST_LIMIT]
        text_subset = self.text[:settings.QUICK_TEST_LIMIT]
        self.model.train()
        assert self.model.fit_done

        pred = self.model.predict(text_subset[0])

    def scoring_accuracy(self):
        random.seed(1)
        self.model.train()
        assert self.model.fit_done
        assert self.model.cv_score <= self.expected_mae_max

        log.info("CV Score: {0}".format(self.model.cv_score))

class PolarityTest(ScanTest, GenericTest):
    loader = PolarityLoader
    data_path = "polarity"

    expected_mae_max = 1

    def setUp(self):
        super(PolarityTest, self).setUp()
        scores, text = self.load_data()
        self.generic_setup(scores, text)
        self.model = Scorer(self.text, self.scores)

    def test_model_creation_and_grading(self):
        self.model_creation_and_grading()

    def test_scoring_accuracy(self):
        self.scoring_accuracy()