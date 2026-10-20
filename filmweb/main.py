"""filmweb

Usage:
    filmweb [--format=<fileformat>]... [--type=<titletype>]... [--workers=<n>] [--pages=<range>] [--debug] <username> <cookie>

Options:
    -h --help                     Show this screen
    -f --format=<fileformat>      Output file format: json (default), csv, letterboxd
    -t --type=<titletype>         Title type: movie, tv_show, game (default: all)
    -w --workers=<n>              Number of parallel workers (default: CPU count)
    -p --pages=<range>            Fetch only given pages of ratings list (100 titles per page),
                                  e.g. 3 or 2-5 or 4- (default: all pages)
    -d --debug                    Debug prints

Source:
    https://github.com/ppatrzyk/filmweb-export
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

CPU_COUNT = multiprocessing.cpu_count()
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

def _parse_pages(raw_pages):
    """Parse --pages value into (first, last) tuple, last=None means 'to the end'"""
    if raw_pages is None:
        return (1, None)
    match = re.fullmatch(r"\s*(\d+)\s*(-\s*(\d*))?\s*", raw_pages)
    assert match, f"--pages must look like 3, 2-5 or 4-, got: {raw_pages}"
    first = int(match.group(1))
    if match.group(2) is None:
        last = first
    else:
        last = int(match.group(3)) if match.group(3) else None
    assert first >= 1, "--pages must start at page 1 or later"
    assert last is None or last >= first, "--pages range end must not be lower than its start"
    return (first, last)

def _resolve_workers(raw_workers):
    """Number of parallel workers: CPU count by default"""
    if raw_workers is None:
        return CPU_COUNT
    try:
        workers = int(raw_workers)
        assert workers >= 1, "--workers must be at least 1"
        if workers > CPU_COUNT:
            logging.warning(f"--workers={workers} exceeds CPU count ({CPU_COUNT})")
        return workers
    except ValueError:
        raise AssertionError(f"--workers must be positive integer, got: {raw_workers}")

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
    first_page, last_page = _parse_pages(args["--pages"])
    workers = _resolve_workers(args["--workers"])
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
            end_page = pages if last_page is None else min(last_page, pages)
            if first_page > end_page:
                logging.info(f"Skipping {title_type}, requested pages start after last page ({pages})")
                continue
            pages_to_fetch = end_page - first_page + 1
            logging.info(f"Fetching list of {title_type} ratings (pages {first_page}-{end_page} of {pages})...")
            get_titles_page_args = ((cookie, user, friend_query, api_title_type, page) for page in range(first_page, end_page+1))
            user_ratings_raw = tuple(tqdm.tqdm(pool.imap_unordered(getter.get_titles_page, get_titles_page_args), total=pages_to_fetch))
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
