from setuptools import setup

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='cbpi4-pt100x',
      version='0.2.0',
      description='CraftBeerPi4 PT100/PT1000 Sensor Plugin',
      author='Alexander Vollkopf',
      author_email='avollkopf@web.de',
      url='https://github.com/PiBrewing/cbpi4-pt100x',
      include_package_data=True,
      package_data={
        # If any package contains *.txt or *.rst files, include them:
      '': ['*.txt', '*.rst', '*.yaml'],
      'cbpi4-pt100x': ['*','*.txt', '*.rst', '*.yaml']},
      packages=['cbpi4-pt100x'],
      long_description=long_description,
      long_description_content_type='text/markdown',
      install_requires=[
          'adafruit-circuitpython-max31865'
      ], 
     )
