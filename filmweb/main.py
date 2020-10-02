"""filmweb

Usage:
    filmweb get <username>

Options:
    -h --help        Show this screen.
"""

from docopt import docopt
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
    write_data,
)

PARALLEL_PROC = 4
MOVIES_PER_PAGE = 25

def main(user, password):
    # args= docopt(__doc__)
    # print('main called')
    # print(args)
    # user = None
    # password = None
    data_format = 'json'
    session = requests.session()
    login(session, user, password)
    votes = get_vote_count(get_page(session, user))
    pages = ceil(votes/MOVIES_PER_PAGE)
    pool = Pool(processes=PARALLEL_PROC)
    get_page_args = ((deepcopy(session), user, page) for page in range(1, pages+1))
    raw_responses = tuple(tqdm.tqdm(pool.starmap(get_page, get_page_args), total=pages))
    movies = tuple(tqdm.tqdm(pool.map(get_movie_ratings, raw_responses), total=pages))
    pool.close()
    print(movies)
    logout(session)
    session.cookies.clear()
    session.close()
    write_data(movies, data_format)


if __name__ == "__main__":
    main()
