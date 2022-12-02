# ! important
# see https://stackoverflow.com/a/27868004/1497139
from setuptools import setup
from collections import OrderedDict

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='py-sidif',
    version='0.0.10',

    packages=['sidif',],
    author='Wolfgang Fahl',
    author_email='wf@bitplan.com',
    maintainer='Wolfgang Fahl',
    url='https://github.com/WolfgangFahl/py-sidif',
    project_urls=OrderedDict(
        (
            ("Documentation", "http://wiki.bitplan.com/index.php/py-sidif"),
            ("Code", "https://github.com/WolfgangFahl/py-sidif/blob/main/sidif/sidif.py"),
            ("Issue tracker", "https://github.com/WolfgangFahl/py-sidif/issues"),
        )
    ),
    license='Apache License',
    description='python SiDIF Simple Data Interchange Format Parser library',
    install_requires=[
          'pyparsing'
    ],
    classifiers=[
            'Programming Language :: Python',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
            'Programming Language :: Python :: 3.10',
            'Programming Language :: Python :: 3.11'
 
    ],
    long_description=long_description,
    long_description_content_type='text/markdown'
)
