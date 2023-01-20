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
from . import getter
from . import parser

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
        votes_total = getter.get_votes_count(user)
        pages = ceil(votes_total/MOVIES_PER_PAGE)
        logged_in_user = getter.auth_check(cookie)
        friend_query = (user != logged_in_user)
        logging.info('Fetching list of movies...')
        get_films_page_args = ((cookie, user, page) for page in range(1, pages+1))
        raw_responses = tuple(tqdm.tqdm(pool.imap_unordered(getter.get_films_page, get_films_page_args), total=pages))
        logging.info('Parsing list of movies...')
        ids = tuple(tqdm.tqdm(pool.imap_unordered(parser.extract_movie_ids, raw_responses), total=pages))
        ids = tuple(set(itertools.chain.from_iterable((json.loads(el) for el in ids))))
        total_movies = len(ids)
        logging.info(f'User {user} has {total_movies} movies...')
        logging.info('Fetching movie details...')
        logging.info('Fetching user ratings [1/3]...')
        get_user_rating_args = ((cookie, movie_id, user, friend_query) for movie_id in ids)
        user_ratings = tuple(tqdm.tqdm(pool.imap_unordered(getter.get_user_rating, get_user_rating_args), total=total_movies))
        # TODO make these 2 optional?
        logging.info('Fetching info about movies [2/3]...')
        global_info = tuple(tqdm.tqdm(pool.imap_unordered(getter.get_global_info, ids), total=total_movies))
        logging.info('Fetching global rating for movies [3/3]...')
        global_rating = tuple(tqdm.tqdm(pool.imap_unordered(getter.get_global_rating, ids), total=total_movies))
        movies = parser.merge_data(ids, user_ratings, global_info, global_rating)
        logging.info('Writing data...')
        parser.write_data(movies, user, file_format)
    except Exception as e:
        logging.error(f'Program error: {str(e)}')
    finally:
        pool.close()

if __name__ == "__main__":
    main()
