from setuptools import setup, find_packages
import sys, os

version = '0.0'

setup(name='sqlusers',
      version=version,
      description="",
      long_description=""" """,
      classifiers=[],
      keywords='',
      author='',
      author_email='',
      url='',
      license='',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'dolmen.batch',
          'dolmen.sqlcontainer',
          'psycopg2',
          'siguvtheme.uvclight',
          'uvclight[auth]',
          'uvclight[sql]',
          'zope.testing',
      ],
      entry_points={
         'fanstatic.libraries': [
            'sqlusers = sqlusers.resources:library',
         ],
         'paste.app_factory': [
             'app = sqlusers.utils:MySQL.create',
         ],
        'pytest11': [
            'sql_fixtures = sqlusers.tests.fixtures',
        ]
      }
      )
