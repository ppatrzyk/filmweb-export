"""filmweb

Usage:
    filmweb <username> <password> [--format=<fileformat>] [--get_user=<username>] [--debug]

Options:
    -h --help                     Show this screen
    -f --format=<fileformat>      Output file format: csv (default) or json
    -u --get_user=<username>      User whose ratings are fetched (default: user logging in)
    -d --debug                    Debug prints
"""

from docopt import docopt
import logging
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

def main():
    args = docopt(__doc__)
    user = args['<username>']
    password = args['<password>']
    file_format = (args['--format'] or 'csv').lower()
    assert file_format in ('csv', 'json'), 'Supported file formats: csv, JSON'
    get_user = args['--get_user'] or user
    if args['--debug']:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    session = requests.session()
    login(session, user, password)
    votes = get_vote_count(session, get_user)
    pages = ceil(votes/MOVIES_PER_PAGE)
    pool = Pool(processes=PARALLEL_PROC)
    get_page_args = ((deepcopy(session), get_user, page) for page in range(1, pages+1))
    logging.info('Fetching data...')
    raw_responses = tuple(tqdm.tqdm(pool.imap_unordered(get_page, get_page_args), total=pages))
    logging.info('Parsing data...')
    movies = tuple(pool.map(get_movie_ratings, raw_responses))
    pool.close()
    logout(session)
    session.cookies.clear()
    session.close()
    file_name = write_data(movies, get_user, file_format)
    logging.info(f'{file_name} written!')

if __name__ == "__main__":
    main()
