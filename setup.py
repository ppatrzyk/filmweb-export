from distutils.core import setup

setup(name='filmweb',
    version='0.0.1',
    description='todo',
    author='Piotr Patrzyk',
    author_email='todo',
    url='todo',
    packages=['filmweb'],
    entry_points={
        'console_scripts': [
            'filmweb=filmweb.main:main',
        ],
    },
)