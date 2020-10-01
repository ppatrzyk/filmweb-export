"""filmweb

Usage:
    filmweb get <username>

Options:
    -h --help        Show this screen.
"""

from docopt import docopt
from math import ceil
import requests
from multiprocessing import Pool
import tqdm
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
    pool = Pool(processes=4)
    raw_responses = tuple(tqdm.tqdm(pool.imap_unordered(get_page, range(1, pages+1)), total=pages))
    movies = tuple(tqdm.tqdm(pool.imap_unordered(get_movie_ratings, raw_responses), total=pages))
    print(movies)
    logout(session)
    session.cookies.clear()
    session.close()

if __name__ == "__main__":
    main()
