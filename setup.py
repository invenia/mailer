from __future__ import absolute_import
from distutils.core import setup

setup(
    name='mailer',
    version='0.2.0',
    author='Brendan Curran-Johnson',
    author_email='brendan.curran.johnson@invenia.ca',
    packages=['mailer', 'mailer.test'],
    scripts=[],  # don't forget to add a script
    url='https://pip.invenia.ca/sample/mailer',
    license='LICENSE.txt',
    description='Email sending functions.',
    install_requires=[
    ],
)
