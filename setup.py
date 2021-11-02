from setuptools import setup

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setup(name='filmweb',
    version='0.5',
    license='MIT',
    description='Export movie ratings from filmweb.pl',
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=['filmweb', 'movie', 'crawler'],
    author='Piotr Patrzyk',
    url='https://github.com/ppatrzyk/filmweb-export',
    packages=['filmweb'],
    python_requires='>=3.6',
    install_requires=[
        'beautifulsoup4>=4.10.0',
        'docopt>=0.6.2',
        'requests>=2.26.0',
        'tqdm>=4.62.3',
    ],
    entry_points={
        'console_scripts': [
            'filmweb=filmweb.main:main',
        ],
    },
)