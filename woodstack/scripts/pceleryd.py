#!/usr/bin/env python
import os
import sys
from celery.bin.celeryd import WorkerCommand
from pyramid.paster import bootstrap
from woodstack.task import pcelery

def usage(argv):# pragma: no cover 
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [options]\n'
          '(example: "%s development.ini" -l info)' % (cmd, cmd)) 
    sys.exit(1)

def pcelery_setup(config_uri):
    config = bootstrap(config_uri)
    pcelery.config_celery(config['registry'].settings)

def main(argv=sys.argv): # pragma: no cover
    if len(argv) < 2:
        usage(argv)

    config_uri = argv[1]
    pcelery_setup(config_uri)

    worker = WorkerCommand(app=pcelery.celery)
    worker.execute_from_commandline(argv=argv[1:])

if __name__ == "__main__": # pragma: no cover
    main()
