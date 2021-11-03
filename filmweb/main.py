"""filmweb

Usage:
    filmweb [--format=<fileformat>] [--debug] <username> <cookie>

Options:
    -h --help                     Show this screen
    -f --format=<fileformat>      Output file format: json (default), csv, all (writes both)
    -d --debug                    Debug prints
"""

from docopt import docopt
import logging
from math import ceil
import multiprocessing
import tqdm
from .getter import (
    get_page,
    get_vote_count,
)
from .parser import (
    extract_movie_ratings,
    write_data,
)

PARALLEL_PROC = multiprocessing.cpu_count()
MOVIES_PER_PAGE = 25

def main():
    args = docopt(__doc__)
    user = args['<username>']
    cookie = args['<cookie>']
    file_format = (args['--format'] or 'json').lower()
    assert file_format in ('all', 'csv', 'json'), 'Supported file formats: all, csv, JSON'
    if args['--debug']:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    pool = multiprocessing.Pool(processes=PARALLEL_PROC)
    try:
        get_vote_count_kwargs = {
            'cookie': cookie,
            'user': user,
        }
        votes = get_vote_count(**get_vote_count_kwargs)
        pages = ceil(votes/MOVIES_PER_PAGE)
        get_page_args = ((cookie, user, page) for page in range(1, pages+1))
        logging.info('Fetching data...')
        raw_responses = tuple(tqdm.tqdm(pool.imap_unordered(get_page, get_page_args), total=pages))
        logging.info('Parsing data...')
        movies = tuple(tqdm.tqdm(pool.imap_unordered(extract_movie_ratings, raw_responses), total=pages))
        write_data(movies, user, file_format)
    except Exception as e:
        logging.error(f'Program error: {str(e)}')
    finally:
        pool.close()

if __name__ == "__main__":
    main()
