"""filmweb

Usage:
    filmweb details [--format=<fileformat>]... [--workers=<n>] [--debug] <id>...
    filmweb [--format=<fileformat>]... [--type=<titletype>]... [--workers=<n>] [--pages=<range>] [--since=<date>] [--debug] <username> <cookie>

Options:
    -h --help                     Show this screen
    -f --format=<fileformat>      Output file format: json (default), csv, letterboxd
    -t --type=<titletype>         Title type: movie, tv_show, game (default: all)
    -w --workers=<n>              Number of parallel workers (default: CPU count)
    -p --pages=<range>            Fetch only given pages of ratings list (100 titles per page),
                                  e.g. 3 or 2-5 or 4- (default: all pages)
    -s --since=<date>             Export only titles rated (or re-rated) on or after
                                  given date, inclusive, format YYYY-MM-DD
                                  (default: all titles)
    -d --debug                    Debug prints

Source:
    https://github.com/ppatrzyk/filmweb-export
"""

import itertools
import json
import logging
import multiprocessing
import re
from datetime import datetime
from math import ceil

import tqdm
from docopt import docopt

from . import getter, parser

logger = logging.getLogger(__name__)

CPU_COUNT = multiprocessing.cpu_count()
MOVIES_PER_PAGE = 100
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
    for title_type in raw_types or DEFAULT_TITLE_TYPES:
        key = title_type.lower().strip()
        resolved_types = (
            DEFAULT_TITLE_TYPES if key == "all" else (TITLE_TYPE_ALIASES.get(key),)
        )
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
    assert last is None or last >= first, (
        "--pages range end must not be lower than its start"
    )
    return (first, last)


def _parse_since(raw_since):
    """
    Parse --since value (YYYY-MM-DD) into timestamp in ms, None means 'no limit'.
    The day is inclusive: the limit is local midnight, the same timezone
    that is used for the `date` column in the output.
    """
    if raw_since is None:
        return 0
    try:
        since = datetime.strptime(raw_since.strip(), "%Y-%m-%d")
    except ValueError:
        raise AssertionError(f"--since must look like 2026-10-19, got: {raw_since}")
    return int(since.timestamp() * 1000)


def _resolve_workers(raw_workers):
    """Number of parallel workers: CPU count by default"""
    if raw_workers is None:
        return CPU_COUNT
    try:
        workers = int(raw_workers)
        assert workers >= 1, "--workers must be at least 1"
        if workers > CPU_COUNT:
            logger.warning(f"--workers={workers} exceeds CPU count ({CPU_COUNT})")
        return workers
    except ValueError:
        raise AssertionError(f"--workers must be positive integer, got: {raw_workers}")


def _parse_ids(raw_ids):
    """Parse title ids given to details command, drop duplicates, keep order"""
    for raw_id in raw_ids:
        assert raw_id.isdigit(), f"Title id must be a number, got: {raw_id}"
    return tuple(dict.fromkeys(int(raw_id) for raw_id in raw_ids))


def _get_details(ids, pool):
    """Fetch details for given ids"""
    details = tuple(
        json.loads(el)
        for el in tqdm.tqdm(
            pool.imap_unordered(getter.get_details, ids), total=len(ids)
        )
    )
    details = tuple(parser.parse_details(d) for d in details)
    return details


def details(args, pool):
    """Get extended info about titles with given ids"""
    ids = _parse_ids(args["<id>"])
    formats = {f.lower() for f in (args["--format"] or ("json",))}
    supported_formats = {"csv", "json"}
    assert formats and formats.issubset(supported_formats), (
        f"Supported file formats: {supported_formats}"
    )
    logger.info("Fetching details...")
    details = _get_details(ids, pool)
    movies = parser.merge_data(
        ids,
        [
            details,
        ],
    )
    parser.write_details(movies, formats)


def user_export(args, pool):
    """
    Export user data
    """
    user = args["<username>"]
    cookie = args["<cookie>"]
    assert all([user, cookie]), "Empty arguments provided"
    formats = {f.lower() for f in (args["--format"] or ("json",))}
    supported_formats = {"csv", "json", "letterboxd"}
    assert formats and formats.issubset(supported_formats), (
        f"Supported file formats: {supported_formats}"
    )
    title_types = _normalize_title_types(args["--type"])
    first_page, last_page = _parse_pages(args["--pages"])
    raw_since = args["--since"]
    since_ms = _parse_since(raw_since)
    cookie = re.sub("Cookie:", "", cookie).strip()
    logged_in_user = getter.auth_check(cookie)
    friend_query = user != logged_in_user
    user_ratings_by_type = []
    logger.info("Fetching list of rated titles [1/4]...")
    for title_type in title_types:
        api_title_type = TITLE_TYPE_TO_API[title_type]
        votes_total = getter.get_votes_count(user, api_title_type)
        pages = ceil(votes_total / MOVIES_PER_PAGE)
        if pages == 0:
            logger.info(f"Skipping {title_type}, no ratings found")
            continue
        end_page = pages if last_page is None else min(last_page, pages)
        if first_page > end_page:
            logger.info(
                f"Skipping {title_type}, requested pages start after last page ({pages})"
            )
            continue
        pages_to_fetch = end_page - first_page + 1
        logger.info(
            f"Fetching list of {title_type} ratings (pages {first_page}-{end_page} of {pages})..."
        )
        get_titles_page_args = (
            (cookie, user, friend_query, api_title_type, page)
            for page in range(first_page, end_page + 1)
        )
        user_ratings_raw = tuple(
            tqdm.tqdm(
                pool.imap_unordered(getter.get_titles_page, get_titles_page_args),
                total=pages_to_fetch,
            )
        )
        user_ratings_by_type.append(
            tuple(
                itertools.chain.from_iterable(json.loads(el) for el in user_ratings_raw)
            )
        )
    user_ratings = tuple(
        el
        for el in itertools.chain.from_iterable(user_ratings_by_type)
        if el.get("timestamp", 0) >= since_ms
    )
    total_titles = len(user_ratings)
    since_msg = "" if raw_since is None else f" since {raw_since}"
    logger.info(f"User {user} has {total_titles} rated titles{since_msg}...")
    assert total_titles, "No rated titles available"
    ids = tuple(el.get("movie_id") for el in user_ratings)
    logger.info("Fetching info about titles [2/4]...")
    details = _get_details(ids, pool)
    logger.info("Fetching global rating for titles [3/4]...")
    global_rating = tuple(
        json.loads(el)
        for el in tqdm.tqdm(
            pool.imap_unordered(getter.get_global_rating, ids), total=total_titles
        )
    )
    logger.info("Writing data [4/4]...")
    movies = parser.merge_data(ids, [user_ratings, details, global_rating])
    parser.write_user_export(movies, user, formats)


def main():
    args = docopt(__doc__)
    if args["--debug"]:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    workers = _resolve_workers(args["--workers"])
    pool = multiprocessing.Pool(processes=workers)
    try:
        if args["details"]:
            details(args, pool)
        else:
            user_export(args, pool)
    except Exception as e:  # noqa
        logger.error(f"Program error: {e!s}")
    finally:
        pool.close()


if __name__ == "__main__":
    main()
