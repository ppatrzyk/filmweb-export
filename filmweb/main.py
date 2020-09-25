"""filmweb

Usage:
    filmweb get <username>

Options:
    -h --help        Show this screen.
"""

from docopt import docopt

def main():
    args= docopt(__doc__)
    print('main called')
    print(args)

if __name__ == "__main__":
    main()
