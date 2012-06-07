Woodstack
=========

Introduction
------------

This is a web stack that intergrates several exisitng tools into pyramid.

*mongo*
- use [mongoengine](https://github.com/MongoEngine/mongoengine) for MongoDB ORM
- REST interface with traversal pattern
- gevent supported

*task*
- use [celery](https://github.com/ask/celery>) for distributed task queue
- Copped with mongodb
- Decorator that speficy queue name and auto register tasks
- configure and run celeryd with paste script, $ pceleryd [development.ini]
- REST interface

*rest*
- Rest Contract and Views

demo
----
The demo inlcudes a html5 website template with backbone and bootstrap.
