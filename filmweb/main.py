"""filmweb

Usage:
    filmweb [--format=<fileformat>] [--debug] <username> <cookie>

Options:
    -h --help                     Show this screen
    -f --format=<fileformat>      Output file format: json (default), csv, all (writes both)
    -d --debug                    Debug prints
"""

from docopt import docopt
import itertools
import json
import re
import logging
from math import ceil
import multiprocessing
import tqdm
from .getter import (
    auth_check,
    get_films_page,
    get_votes_count,
)
from .parser import (
    extract_movie_ids,
    write_data,
)

PARALLEL_PROC = multiprocessing.cpu_count()
MOVIES_PER_PAGE = 25

def main():
    args = docopt(__doc__)
    user = args['<username>']
    cookie = args['<cookie>']
    assert all([user, cookie]), 'Empty arguments provided'
    file_format = (args['--format'] or 'json').lower()
    assert file_format in ('all', 'csv', 'json'), 'Supported file formats: all, csv, JSON'
    if args['--debug']:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    pool = multiprocessing.Pool(processes=PARALLEL_PROC)
    try:
        logging.info('Checking args...')
        cookie = re.sub('Cookie:', '', cookie).strip()
        votes_total = get_votes_count(user)
        pages = ceil(votes_total/MOVIES_PER_PAGE)
        # get_films_page((cookie, user, 1))
        auth_check(cookie)
        logging.info('Fetching list of movies...')
        get_films_page_args = ((cookie, user, page) for page in range(1, pages+1))
        raw_responses = tuple(tqdm.tqdm(pool.imap_unordered(get_films_page, get_films_page_args), total=pages))
        logging.info('Parsing list of movies...')
        ids = tuple(tqdm.tqdm(pool.imap_unordered(extract_movie_ids, raw_responses), total=pages))
        ids = set(itertools.chain.from_iterable((json.loads(el) for el in ids)))
        logging.info('Fetching movie details...')
        # 2 query api for data about each film
        print(len(ids))
        # write_data(movies, user, file_format)
    except Exception as e:
        logging.error(f'Program error: {str(e)}')
    finally:
        pool.close()

if __name__ == "__main__":
    main()
