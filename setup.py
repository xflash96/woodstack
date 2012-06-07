import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = ['pyramid', 'pyramid_debugtoolbar', 'mongoengine', 'gevent', 'celery', 'webtest']

setup(name='woodstack',
      version='0.02',
      description='web stack for pyramid',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Po-Wei Wang',
      author_email='xflash96@gmail.com',
      url='https://github.com/xflash96/woodstack',
      keywords='web pyramid pylons',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="",
      entry_points = """\
      [console_scripts]
      pceleryd = woodstack.scripts.pceleryd:main
      """,
      paster_plugins=['pyramid'],
      )

