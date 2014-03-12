import hashlib
from sqlalchemy import event
from scan.log import logging
from datetime import datetime
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import UserMixin, RoleMixin
from scan import settings

log = logging.getLogger(__name__)
db = SQLAlchemy()

STRING_MAX = 255

roles_users = db.Table('roles_users', db.Model.metadata,
                       db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(STRING_MAX), unique=True)
    description = db.Column(db.String(STRING_MAX))

    def __repr__(self):
        return "<Role(name='%s')>" % (self.name)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(STRING_MAX))
    last_name = db.Column(db.String(STRING_MAX))
    username = db.Column(db.String(STRING_MAX), unique=True)
    email = db.Column(db.String(STRING_MAX), unique=True)
    password = db.Column(db.String(STRING_MAX))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime(timezone=True))
    hashkey = db.Column(db.String(STRING_MAX), unique=True)

    created = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated = db.Column(db.DateTime(timezone=True), onupdate=datetime.utcnow)

    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

    def __repr__(self):
        return "<User(name='%s', lastname='%s', password='%s')>" % (self.username, self.last_name, self.password)

class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(STRING_MAX))
    description = db.Column(db.Text)
    prompt = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    user = db.relationship("User", backref=db.backref('questions', order_by=id))

    created = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated = db.Column(db.DateTime(timezone=True), onupdate=datetime.utcnow)

class Essay(db.Model):
    __tablename__ = 'essays'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)
    actual_score = db.Column(db.Float)
    info = db.Column(db.Text)

    predicted_score = db.Column(db.Float)
    model_id = db.Column(db.Integer, db.ForeignKey('models.id'))
    model = db.relationship("Model", backref=db.backref('essays', order_by=id))

    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))
    question = db.relationship("Question", backref=db.backref('essays', order_by=id))

    created = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated = db.Column(db.DateTime(timezone=True), onupdate=datetime.utcnow)

class PredictedScore(db.Model):
    __tablename__ = 'predictedscores'

    id = db.Column(db.Integer, primary_key=True)
    prediction = db.Column(db.Float)
    version = db.Column(db.Integer)

    essay_id = db.Column(db.Integer, db.ForeignKey('essays.id'))
    essay = db.relationship("Essay", backref=db.backref('predicted_scores', order_by=id))

    model_id = db.Column(db.Integer, db.ForeignKey('models.id'))
    model = db.relationship("Model", backref=db.backref('predicted_scores', order_by=id))

    created = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated = db.Column(db.DateTime(timezone=True), onupdate=datetime.utcnow)

class Model(db.Model):
    __tablename__ = 'models'

    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.Text)

    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))
    question = db.relationship("Question", backref=db.backref('models', order_by=id))

    version = db.Column(db.Integer(), default=settings.MODEL_VERSION)
    error = db.Column(db.Float)

    created = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated = db.Column(db.DateTime(timezone=True), onupdate=datetime.utcnow)