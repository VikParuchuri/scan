from flask_wtf import Form
from wtforms import FloatField, IntegerField, TextField, StringField, TextAreaField


class QuestionForm(Form):
    name = StringField('Name', description="The name you want to give this question.")
    prompt = TextAreaField('Prompt', description="The prompt for this question (optional).")


