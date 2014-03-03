from scan import settings
import re
import os

class BaseCorrector(object):
    def __init__(self):
        self.data = file(os.path.join(settings.DATA_PATH, "big.txt")).read()

    def words(self, text):
        return re.findall('[a-z]+', text.lower())