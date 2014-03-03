from flask import Blueprint, render_template, abort, request, url_for
from werkzeug.utils import redirect
from core.web.forms import QuestionForm
from scan import settings
import os
from flask.ext.security import login_required
from flask.ext.login import current_user
import json
from flask.views import MethodView

main_views = Blueprint('main_views', __name__, template_folder=os.path.join(settings.REPO_PATH, 'templates'))

@main_views.route('/')
def index():
    return render_template("index.html")

@main_views.route('/question_list')
def question_list():
    form_obj = QuestionForm()
    form = render_template("forms/question.html", form=form_obj)
    return render_template("questions.html", questions=current_user.questions, form=form)

class Question(MethodView):
    decorators = [login_required]

    def post(self):
        form_obj = QuestionForm()
        if form_obj.validate_on_submit():
            return redirect(url_for('main_views.question_list'))
        form_obj = QuestionForm()
        form = render_template("forms/question.html", form=form_obj)
        return render_template("questions.html", questions=current_user.questions, form=form)

main_views.add_url_rule('/question', view_func=Question.as_view('question'))