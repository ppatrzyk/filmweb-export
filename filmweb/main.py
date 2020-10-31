"""filmweb

Usage:
    filmweb <username> <password> [--format=<fileformat>] [--get_user=<username>] [--debug]

Options:
    -h --help                     Show this screen
    -f --format=<fileformat>      Output file format: json (default), csv, all (writes both)
    -u --get_user=<username>      User whose ratings are fetched (default: user logging in)
    -d --debug                    Debug prints
"""

from docopt import docopt
import logging
from math import ceil
from copy import deepcopy
import requests
import multiprocessing
import tqdm
from .utils import (
    get_movie_ratings,
    get_page,
    get_vote_count,
    get_user_id,
    login,
    logout,
    write_data,
)

PARALLEL_PROC = multiprocessing.cpu_count()
MOVIES_PER_PAGE = 25

def main():
    args = docopt(__doc__)
    user = args['<username>']
    password = args['<password>']
    file_format = (args['--format'] or 'json').lower()
    assert file_format in ('all', 'csv', 'json'), 'Supported file formats: all, csv, JSON'
    get_user = args['--get_user'] or user
    if args['--debug']:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    session = requests.session()
    pool = multiprocessing.Pool(processes=PARALLEL_PROC)
    try:
        login(session, user, password)
        get_vote_count_kwargs = {
            'session': session,
            'user': get_user,
            'friend_check': None
        }
        if user != get_user:
            user_id = get_user_id(session, user)
            get_vote_count_kwargs['friend_check'] = user_id
        votes = get_vote_count(**get_vote_count_kwargs)
        pages = ceil(votes/MOVIES_PER_PAGE)
        get_page_args = ((deepcopy(session), get_user, page) for page in range(1, pages+1))
        logging.info('Fetching data...')
        raw_responses = tuple(tqdm.tqdm(pool.imap_unordered(get_page, get_page_args), total=pages))
        logging.info('Parsing data...')
        movies = tuple(tqdm.tqdm(pool.imap_unordered(get_movie_ratings, raw_responses), total=pages))
        logout(session)
        write_data(movies, get_user, file_format)
    except Exception as e:
        logging.error(f'Program error: {str(e)}')
    finally:
        pool.close()
        session.cookies.clear()
        session.close()

if __name__ == "__main__":
    main()
