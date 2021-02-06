from setuptools import setup

setup(name='cbpi4-pt100x',
      version='0.0.1',
      description='CraftBeerPi Plugin',
      author='Alexander Vollkopf',
      author_email='',
      url='https://github.com/avollkopf/cbpi4-pt100x',
      include_package_data=True,
      package_data={
        # If any package contains *.txt or *.rst files, include them:
      '': ['*.txt', '*.rst', '*.yaml'],
      'cbpi4-pt100x': ['*','*.txt', '*.rst', '*.yaml']},
      packages=['cbpi4-pt100x'],
     )