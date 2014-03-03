import functools
from celery.signals import worker_shutdown
from app import cache

def single_instance_task():
    def task_exc(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            lock_id = "celery-single-instance-" + func.__name__
            check_lock = lambda: cache.get(lock_id)
            acquire_lock = lambda: cache.set(lock_id, True)
            release_lock = lambda: cache.delete(lock_id)
            if check_lock:
                acquire_lock()
                try:
                    func(*args, **kwargs)
                finally:
                    release_lock()
        return wrapper
    return task_exc


@worker_shutdown.connect
def clear_cache_before_shutdown():
    cache.clear()

