import pcelery
from pcelery import task
from subprocess import Popen, PIPE

def register_task_name(func, name=None):
    if hasattr(func, 'request'):
        id = func.request.id
        backend = pcelery.celery.backend
        db = backend._get_database()
        taskmeta_collection = db[backend.mongodb_taskmeta_collection]
        if not name:
            name = func.name
        taskmeta_collection.update({'_id': id}, {'$set': {'task_name': name}})

@task(name='tasks.add')
def add(x,y):
    register_task_name(add)
    return x*y

@task()
def sub(x,y):
    return x+y

def do_command(args):
    p = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    (out, err) = p.communicate()
    p.wait()
    return out, err

@task()
def get_memory_usage():
    out, err = do_command('wmem')
    return out
