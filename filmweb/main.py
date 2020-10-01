"""filmweb

Usage:
    filmweb get <username>

Options:
    -h --help        Show this screen.
"""

from docopt import docopt
from math import ceil
import requests
from utils import (
    get_movie_ratings,
    get_page,
    get_vote_count,
    login,
    logout,
)

MOVIES_PER_PAGE = 25

def main():
    args= docopt(__doc__)
    print('main called')
    print(args)
    user = None
    password = None
    session = requests.session()
    login(session, user, password)
    votes = get_vote_count(get_page(session, user))
    pages = ceil(votes/MOVIES_PER_PAGE)
    logout(session)
    session.cookies.clear()
    session.close()

if __name__ == "__main__":
    main()
