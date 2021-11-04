"""filmweb

Usage:
    filmweb [--format=<fileformat>] [--debug] <username> <cookie>

Options:
    -h --help                     Show this screen
    -f --format=<fileformat>      Output file format: json (default), csv, all (writes both)
    -d --debug                    Debug prints
"""

from docopt import docopt
import re
import logging
import multiprocessing
import tqdm
from .getter import (
    get_films_page,
    get_profile_page,
)
from .parser import (
    auth_check,
    extract_movie_ratings,
    get_pages_count,
    write_data,
)

PARALLEL_PROC = multiprocessing.cpu_count()

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
        pages = get_pages_count(get_profile_page(user))
        auth_check(get_films_page((cookie, user, 1)))
        logging.info('Fetching data...')
        get_films_page_args = ((cookie, user, page) for page in range(1, pages+1))
        raw_responses = tuple(tqdm.tqdm(pool.imap_unordered(get_films_page, get_films_page_args), total=pages))
        logging.info('Parsing data...')
        movies = tuple(tqdm.tqdm(pool.imap_unordered(extract_movie_ratings, raw_responses), total=pages))
        write_data(movies, user, file_format)
    except Exception as e:
        logging.error(f'Program error: {str(e)}')
    finally:
        pool.close()

if __name__ == "__main__":
    main()
