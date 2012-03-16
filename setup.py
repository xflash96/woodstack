import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = ['pyramid', 'pyramid_debugtoolbar', 'pymongo', 'gevent', 'celery']

setup(name='myapp',
      version='0.0',
      description='myapp',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Po-Wei Wang',
      author_email='xflash96@gmail.com',
      url='https://github.com/xflash96/pyramid_mongo_rest',
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
      [console_scripts]
      pceleryd = myapp.script.celeryd:main
      """,
      paster_plugins=['pyramid'],
      )

