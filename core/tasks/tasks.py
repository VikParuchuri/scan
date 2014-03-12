from app import celery
from core.algo.scorer import Manager
from core.database.models import Question, Essay

class SqlAlchemyTask(celery.Task):
    """An abstract Celery Task that ensures that the connection the the
    database is closed on task completion"""
    abstract = True

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        from app import db
        db.session.remove()

@celery.task(base=SqlAlchemyTask)
def create_model(question_id):
    from app import cache
    question = Question.query.filter_by(id=question_id).first()
    manager = Manager(question)
    manager.create_model()
    cache.delete('{0}_question_status')

@celery.task(base=SqlAlchemyTask)
def score_essay(essay_id):
    from app import db, cache
    essay = Essay.query.filter_by(id=essay_id).first()
    manager = Manager(essay.question)
    score = manager.score_essay(essay)
    essay.predicted_score = score
    essay.model = manager.get_latest_model()
    db.session.commit()

@celery.task(base=SqlAlchemyTask)
def create_and_score(question_id):
    from app import db
    create_model(question_id)
    essay_ids = db.session.query(Essay.id).filter(Essay.question_id == question_id).all()
    for e in essay_ids:
        score_essay(e[0])
