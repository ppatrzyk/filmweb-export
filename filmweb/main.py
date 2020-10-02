"""filmweb

Usage:
    filmweb get <username>

Options:
    -h --help        Show this screen.
"""

from docopt import docopt
import json
from math import ceil
from copy import deepcopy
import requests
from multiprocessing import Pool
import tqdm
from .utils import (
    get_movie_ratings,
    get_page,
    get_vote_count,
    login,
    logout,
)

MOVIES_PER_PAGE = 25

def main(user, password):
    # args= docopt(__doc__)
    # print('main called')
    # print(args)
    # user = None
    # password = None
    session = requests.session()
    login(session, user, password)
    votes = get_vote_count(get_page(session, user))
    pages = ceil(votes/MOVIES_PER_PAGE)
    pool = Pool(processes=4)
    get_page_args = ((deepcopy(session), user, page) for page in range(1, pages+1))
    raw_responses = tuple(tqdm.tqdm(pool.starmap(get_page, get_page_args), total=pages))
    movies = tuple(tqdm.tqdm(pool.map(get_movie_ratings, raw_responses), total=pages))
    print(movies)
    logout(session)
    session.cookies.clear()
    session.close()

if __name__ == "__main__":
    main()
