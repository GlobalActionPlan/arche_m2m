import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

requires = [
    'Arche',
    'pyramid',
    'fanstatic',
    'js.jqueryui',
    'arche_ttw_translation',
    ]

setup(name='arche_m2m',
      version='0.1dev',
      description='Made to Measure',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Development Status :: 3 - Alpha",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='M2M development team and contributors',
      author_email='robin@betahaus.net',
      url='https://github.com/GlobalActionPlan/arche_m2m',
      keywords='web pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="arche_m2m",
      entry_points="""\
      [fanstatic.libraries]
      arche_m2m = arche_m2m.fanstatic:lib_m2m
      """,
      )
