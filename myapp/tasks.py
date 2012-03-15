from pcelery import task
from subprocess import Popen, PIPE

@task()
def add(x,y):
    return x*y

@task()
def sub(x,y):
    return x+y

@task(ignore_result=True)
def do_command(args):
    p = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    (out, err) = p.communicate()
    p.wait()
