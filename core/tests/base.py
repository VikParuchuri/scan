from flask.ext.testing import TestCase
from mock import patch
from app import create_test_app, db
from scan.log import logging

app = create_test_app()
db.app = app
db.init_app(app)

log = logging.getLogger(__name__)

class ScanTest(TestCase):

    def create_app(self):
        return app

    def setUp(self):
        db.create_all(app=app)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
