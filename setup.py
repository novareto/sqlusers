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
          'uvc.themes.btwidgets',
          'dolmen.sqlcontainer',
          'psycopg2',
          'siguvtheme.uvclight',
          'uvclight[auth]',
          'uvclight[sql]',
          'zope.testing',
          'sqlalchemy',
      ],
      entry_points={
         'fanstatic.libraries': [
            'sqlusers = sqlusers.browser.resources:library',
         ],
         'paste.app_factory': [
             'app = sqlusers.utils:SQLApp.create',
         ],
        'pytest11': [
            'sql_fixtures = sqlusers.tests.fixtures',
        ]
      }
      )
