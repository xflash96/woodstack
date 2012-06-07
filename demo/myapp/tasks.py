import gevent.monkey; gevent.monkey.patch_all()
from woodstack.task import task
from subprocess import Popen, PIPE

@task()
def sub(x,y):
    return x+y

def do_command(args):
    p = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    (out, err) = p.communicate()
    p.wait()
    return out, err
