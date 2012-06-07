import monkey
from .resources import TaskItem, TaskCollection
from pcelery import task

import pcelery

def includeme(config):
    config.include('..rest')
    monkey.patch()
    pcelery.config_celery(config.registry.settings)
