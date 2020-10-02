from distutils.core import setup

setup(name='filmweb',
    version='0.1',
    license='MIT',
    description='Export movie ratings from filmweb.pl',
    long_description=open('README.md').read(),
    keywords=['filmweb'],
    author='Piotr Patrzyk',
    author_email='todo',
    url='https://github.com/ppatrzyk/filmweb-export',
    packages=['filmweb'],
    python_requires='~=3.7',
    install_requires=[
        'beautifulsoup4>=4.9.1',
        'certifi>=2020.6.20',
        'chardet>=3.0.4',
        'docopt>=0.6.2',
        'idna>=2.10',
        'requests>=2.24.0',
        'soupsieve>=2.0.1',
        'tqdm>=4.50.0',
        'urllib3>=1.25.10',
    ],
    entry_points={
        'console_scripts': [
            'filmweb=filmweb.main:main',
        ],
    },
)