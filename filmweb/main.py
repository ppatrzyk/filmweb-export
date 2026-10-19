"""filmweb

Usage:
    filmweb [--format=<fileformat>]... [--type=<titletype>]... [--threads=<n>] [--debug] <username> <cookie>

Options:
    -h --help                     Show this screen
    -f --format=<fileformat>      Output file format: json (default), csv, letterboxd
    -t --type=<titletype>         Title type: movie, tv_show, game (default: all)
    -j --threads=<n>              Max number of parallel workers, lowers load on the server
                                  (default: number of CPUs, higher values are capped to it)
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
MOVIES_PER_PAGE = 100
FORMATS = {"csv", "json", "letterboxd"}
DEFAULT_TITLE_TYPES = ("movie", "tv_show", "game")
TITLE_TYPE_TO_API = {"movie": "film", "tv_show": "serial", "game": "videogame"}
TITLE_TYPE_ALIASES = {
    "film": "movie",
    "films": "movie",
    "movie": "movie",
    "movies": "movie",
    "serial": "tv_show",
    "series": "tv_show",
    "show": "tv_show",
    "shows": "tv_show",
    "tv": "tv_show",
    "tvshow": "tv_show",
    "tvshows": "tv_show",
    "tv_show": "tv_show",
    "tv_shows": "tv_show",
    "gra": "game",
    "gry": "game",
    "videogame": "game",
    "videogames": "game",
    "game": "game",
    "games": "game",
}

def _normalize_title_types(raw_types):
    """Normalize user title type values to supported API types"""
    normalized = []
    seen = set()
    for title_type in (raw_types or DEFAULT_TITLE_TYPES):
        key = title_type.lower().strip()
        resolved_types = DEFAULT_TITLE_TYPES if key == "all" else (TITLE_TYPE_ALIASES.get(key), )
        assert all(resolved_types), f"Unsupported title type: {title_type}"
        for resolved in resolved_types:
            if resolved not in seen:
                normalized.append(resolved)
                seen.add(resolved)
    return tuple(normalized)

def _resolve_workers(raw_threads):
    """Number of parallel workers: CPU count by default, user value can only lower it"""
    if raw_threads is None:
        return PARALLEL_PROC
    try:
        threads = int(raw_threads)
    except ValueError:
        raise AssertionError(f"--threads must be an integer, got: {raw_threads}")
    assert threads >= 1, "--threads must be at least 1"
    if threads > PARALLEL_PROC:
        logging.warning(f"--threads={threads} exceeds default ({PARALLEL_PROC}), using {PARALLEL_PROC}")
        return PARALLEL_PROC
    return threads

def main():
    args = docopt(__doc__)
    user = args["<username>"]
    cookie = args["<cookie>"]
    assert all([user, cookie]), "Empty arguments provided"
    formats = set(f.lower() for f in (args["--format"] or ("json", )))
    assert (formats and formats.issubset(FORMATS)), f"Supported file formats: {FORMATS}"
    title_types = _normalize_title_types(args["--type"])
    if args["--debug"]:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    workers = _resolve_workers(args["--threads"])
    pool = multiprocessing.Pool(processes=workers)
    try:
        logging.info("Checking args...")
        cookie = re.sub("Cookie:", "", cookie).strip()
        logged_in_user = getter.auth_check(cookie)
        friend_query = (user != logged_in_user)
        user_ratings_by_type = []
        logging.info("Fetching list of rated titles [1/4]...")
        for title_type in title_types:
            api_title_type = TITLE_TYPE_TO_API[title_type]
            votes_total = getter.get_votes_count(user, api_title_type)
            pages = ceil(votes_total/MOVIES_PER_PAGE)
            if pages == 0:
                logging.info(f"Skipping {title_type}, no ratings found")
                continue
            logging.info(f"Fetching list of {title_type} ratings...")
            get_titles_page_args = ((cookie, user, friend_query, api_title_type, page) for page in range(1, pages+1))
            user_ratings_raw = tuple(tqdm.tqdm(pool.imap_unordered(getter.get_titles_page, get_titles_page_args), total=pages))
            user_ratings_by_type.append(tuple(itertools.chain.from_iterable((json.loads(el) for el in user_ratings_raw))))
        user_ratings = tuple(itertools.chain.from_iterable(user_ratings_by_type))
        total_movies = len(user_ratings)
        logging.info(f"User {user} has {total_movies} rated titles...")
        assert total_movies, "No rated titles available"
        ids = tuple(el.get("entity") for el in user_ratings)
        logging.info("Fetching info about titles [2/4]...")
        global_info = tuple(json.loads(el) for el in tqdm.tqdm(pool.imap_unordered(getter.get_global_info, ids), total=total_movies))
        logging.info("Fetching global rating for titles [3/4]...")
        global_rating = tuple(json.loads(el) for el in tqdm.tqdm(pool.imap_unordered(getter.get_global_rating, ids), total=total_movies))
        logging.info("Writing data [4/4]...")
        movies = parser.merge_data(ids, user_ratings, global_info, global_rating)
        parser.write_data(movies, user, formats)
    except Exception as e:
        logging.error(f"Program error: {str(e)}")
    finally:
        pool.close()

if __name__ == "__main__":
    main()
