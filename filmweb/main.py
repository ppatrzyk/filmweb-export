"""filmweb

Usage:
    filmweb get <username>

Options:
    -h --help        Show this screen.
"""

from docopt import docopt
import requests
from utils import (
    get_movie_ratings,
    get_page,
    get_vote_count,
    login,
)

def main():
    args= docopt(__doc__)
    print('main called')
    print(args)
    session = requests.session()
    # TODO actual stuff here
    session.cookies.clear()
    session.close()

if __name__ == "__main__":
    main()
