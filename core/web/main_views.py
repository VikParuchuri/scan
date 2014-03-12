from celery import states
from flask import Blueprint, render_template, abort, request, url_for, jsonify
from werkzeug.utils import redirect, secure_filename
from core.web.forms import QuestionForm, EssayForm, EssayUploadForm
from scan import settings
import os
from flask.ext.security import login_required, auth_required
from flask.ext.login import current_user
import json
from flask.views import MethodView
from core.database.models import Question, Essay
from celery.utils import get_full_cls_name

main_views = Blueprint('main_views', __name__, template_folder=os.path.join(settings.REPO_PATH, 'templates'))

class InvalidUser(Exception):
    pass

class InvalidAction(Exception):
    pass

@main_views.route('/')
def index():
    return render_template("index.html")

class BaseQuestionView(MethodView):
    decorators = [auth_required('session')]

    def get_model(self, id):
        question = Question.query.filter_by(id=id).first()
        if question.user == current_user:
            return question
        else:
            raise InvalidUser()

    def get_cache_key(self, id):
        return "{0}_question_status".format(id)

    def get_cache(self, id):
        from app import cache
        return cache.get(self.get_cache_key(id))

    def set_cache(self, id, val):
        from app import cache
        return cache.set(self.get_cache_key(id), val)

class QuestionView(BaseQuestionView):
    def get_questions(self):
        questions = current_user.questions
        for q in questions:
            q.status = self.get_cache(q.id)
        return questions

    def get(self):
        form_obj = QuestionForm()
        form = render_template("forms/question.html", form=form_obj)
        return render_template("questions.html", questions=self.get_questions(), form=form)


    def post(self):
        form_obj = QuestionForm()
        if form_obj.validate_on_submit():
            form_obj.save()
            return redirect(url_for('main_views.questions'))
        form = render_template("forms/question.html", form=form_obj)

        return render_template("questions.html", questions=self.get_questions(), form=form)

main_views.add_url_rule('/questions', view_func=QuestionView.as_view('questions'))

class QuestionDetailView(BaseQuestionView):

    def get_upload_form(self, model):
        upload_obj = EssayUploadForm()
        upload_form = render_template("forms/upload.html", form=upload_obj, question=model)
        return upload_form

    def get(self, id):
        model = self.get_model(id)
        form_obj = EssayForm()

        form = render_template("forms/essay.html", form=form_obj, question=model)
        return render_template("question.html", question=model, form=form, status=self.get_cache(id), upload_form=self.get_upload_form(model))

    def post(self, id):
        form_obj = EssayForm()
        model = self.get_model(id)
        if form_obj.validate_on_submit():
            form_obj.save(model)
            return redirect(url_for('main_views.question_detail', id=id))
        form = render_template("forms/essay.html", form=form_obj, question=model)
        return render_template("question.html", question=model, form=form, status=self.get_cache(id), upload_form=self.get_upload_form(model))

    def delete(self, id):
        from app import db
        question = self.get_model(id)
        db.session.delete(question)
        db.session.commit()
        return jsonify({})

main_views.add_url_rule('/question/<int:id>', view_func=QuestionDetailView.as_view('question_detail'))

class QuestionActionView(BaseQuestionView):
    actions = ["create", "create_and_score", ]

    def create(self, model):
        from core.tasks.tasks import create_model
        task_status = create_model.delay(model.id)
        return task_status.id

    def create_and_score(self, model):
        from core.tasks.tasks import create_and_score
        task_status = create_and_score.delay(model.id)
        return task_status.id

    def get(self, id, action):
        model = self.get_model(id)
        if action not in self.actions:
            raise InvalidAction()
        task_id = getattr(self, action)(model)
        self.set_cache(id, url_for('main_views.task_status', task_id=task_id))
        return jsonify({})

main_views.add_url_rule('/question/<int:id>/<string:action>', view_func=QuestionActionView.as_view('question_action'))

class EssayUploadView(BaseQuestionView):

    def post(self, id):
        form_obj = EssayUploadForm()
        if form_obj.validate_on_submit():
            model = self.get_model(id)
            file = request.files['upload']
            form_obj.save(model, file)

        return redirect(url_for('main_views.question_detail', id=id))

main_views.add_url_rule('/question/<int:id>/upload_essays', view_func=EssayUploadView.as_view('essay_upload'))

class BaseEssayView(MethodView):
    decorators = [auth_required('session')]

    def get_model(self, id):
        essay = Essay.query.filter_by(id=id).first()
        if essay.question.user == current_user:
            return essay
        else:
            raise InvalidUser()

    def get_cache_key(self, id):
        return "{0}_essay_status".format(id)

    def get_cache(self, id):
        from app import cache
        return cache.get(self.get_cache_key(id))

    def set_cache(self, id, val):
        from app import cache
        return cache.set(self.get_cache_key(id), val)

class EssayDetailView(BaseEssayView):

    def delete(self, id):
        from app import db
        essay = self.get_model(id)
        db.session.delete(essay)
        db.session.commit()
        return jsonify({})

main_views.add_url_rule('/essay/<int:id>', view_func=EssayDetailView.as_view('essay_detail'))

class EssayActionView(BaseEssayView):
    actions = ["score", ]

    def score(self, model):
        from core.tasks.tasks import score_essay
        task_status = score_essay.delay(model.id)
        return task_status.id

    def get(self, id, action):
        model = self.get_model(id)
        if action not in self.actions:
            raise InvalidAction()
        task_id = getattr(self, action)(model)
        self.set_cache(id, url_for('main_views.task_status', task_id=task_id))
        return jsonify({})

main_views.add_url_rule('/essay/<int:id>/<string:action>', view_func=EssayActionView.as_view('essay_action'))

class TaskStatusView(MethodView):
    decorators = [auth_required('session')]

    def get(self, task_id):
        from app import celery

        result = celery.AsyncResult(task_id)
        state, retval = result.state, result.result
        response_data = dict(id=task_id, status=state)
        if state in states.EXCEPTION_STATES:
            traceback = result.traceback
            response_data.update({'exc': get_full_cls_name(retval.__class__),
                                  'traceback': traceback})
        return jsonify({'task': response_data})

main_views.add_url_rule('/tasks/<string:task_id>', view_func=TaskStatusView.as_view('task_status'))