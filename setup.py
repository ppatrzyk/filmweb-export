from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='filmweb',
    version='0.1',
    license='MIT',
    description='Export movie ratings from filmweb.pl',
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=['filmweb', 'movie', 'crawler'],
    author='Piotr Patrzyk',
    url='https://github.com/ppatrzyk/filmweb-export',
    packages=['filmweb'],
    python_requires='>=3.7',
    install_requires=[
        'beautifulsoup4>=4.9.1',
        'docopt>=0.6.2',
        'requests>=2.24.0',
        'tqdm>=4.50.0',
    ],
    entry_points={
        'console_scripts': [
            'filmweb=filmweb.main:main',
        ],
    },
)