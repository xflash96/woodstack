import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

requires = ['woodstack', 'pyramid', 'pyramid_debugtoolbar', 'mongoengine', 'gevent', 'celery', 'webtest']

setup(name='myapp',
      version='0.02',
      description='myapp',
      long_description=README,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Po-Wei Wang',
      author_email='xflash96@gmail.com',
      keywords='web pyramid pylons',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="myapp",
      entry_points = """\
      [paste.app_factory]
      main = myapp:main
      """,
      paster_plugins=['pyramid'],
      )

