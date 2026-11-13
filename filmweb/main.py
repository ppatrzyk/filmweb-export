"""filmweb

Usage:
    filmweb details [--format=<fileformat>]... [--stdout] [--workers=<n>] [--debug] <id>...
    filmweb search [--format=<fileformat>]... [--stdout] [--type=<titletype>]... [--pages=<range>] [--workers=<n>] [--debug] <query>...
    filmweb [--format=<fileformat>]... [--stdout] [--type=<titletype>]... [--workers=<n>] [--pages=<range>] [--since=<date>] [--debug] <username> <cookie>

Options:
    -h --help                     Show this screen
    -f --format=<fileformat>      Output file format: json (default), csv, letterboxd
    -o --stdout                   Print result to stdout instead of file
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
from math import ceil

import tqdm
from docopt import docopt

from . import getter, parser, writer

logger = logging.getLogger(__name__)

CPU_COUNT = multiprocessing.cpu_count()
MOVIES_PER_PAGE = 100
SEARCH_PAGE_SIZE = 25


def _get_details(ids: tuple[int], pool: multiprocessing.Pool):
    """Fetch details for given ids"""
    details = tuple(
        json.loads(el)
        for el in tqdm.tqdm(
            pool.imap_unordered(getter.get_preview, ids), total=len(ids)
        )
    )
    details = tuple(parser.parse_details(d) for d in details)
    return details


def details(args: dict, pool: multiprocessing.Pool):
    """Get extended info about titles with given ids"""
    ids = parser.parse_ids(args["<id>"])
    logger.info("Fetching info about titles [1/2]...")
    details = _get_details(ids, pool)
    logger.info("Fetching global rating for titles [2/2]...")
    global_rating = tuple(
        json.loads(el)
        for el in tqdm.tqdm(
            pool.imap_unordered(getter.get_global_rating, ids), total=len(ids)
        )
    )
    return parser.merge_data(
        ids,
        [details, global_rating],
    )


def search(args: dict, pool: multiprocessing.Pool):
    """Search titles by text, then get info (incl. poster) about found titles"""
    query = " ".join(args["<query>"]).strip()
    assert query, "Empty search query"
    title_types = parser.normalize_title_types(args["--type"])
    first_page, last_page = parser.parse_pages(args["--pages"])
    logger.info(f"Searching for '{query}'...")
    search_results = []
    for title_type in title_types:
        results_total = getter.search_check_total(query=query, title_type=title_type)
        if results_total == 0:
            logger.info(f"Skipping {title_type}, no results found")
            continue
        pages = ceil(results_total / SEARCH_PAGE_SIZE)
        end_page = pages if last_page is None else min(last_page, pages)
        if first_page > end_page:
            logger.info(
                f"Skipping {title_type}, requested pages start after last page ({pages})"
            )
            continue
        pages_to_fetch = end_page - first_page + 1
        logger.info(
            f"Fetching search results for {title_type} (pages {first_page}-{end_page} of {pages})..."
        )
        search_args = (
            (query, title_type, page, SEARCH_PAGE_SIZE)
            for page in range(first_page, end_page + 1)
        )
        search_raw = tuple(
            tqdm.tqdm(
                pool.imap_unordered(getter.search, search_args),
                total=pages_to_fetch,
            )
        )
        search_results.extend(
            tuple(
                itertools.chain.from_iterable(
                    json.loads(el).get("searchHits", []) for el in search_raw
                )
            )
        )
    movies = tuple(parser.parse_search_entry(entry) for entry in search_results)
    return query, movies


def user_export(args: dict, pool: multiprocessing.Pool):
    """
    Export user data
    """
    user = args["<username>"]
    cookie = args["<cookie>"]
    assert all([user, cookie]), "Empty arguments provided"
    title_types = parser.normalize_title_types(args["--type"])
    first_page, last_page = parser.parse_pages(args["--pages"])
    raw_since = args["--since"]
    since_ms = parser.parse_since(raw_since)
    cookie = re.sub("Cookie:", "", cookie).strip()
    logged_in_user = getter.auth_check(cookie)
    friend_query = user != logged_in_user
    user_ratings_by_type = []
    logger.info("Fetching list of rated titles [1/3]...")
    for title_type in title_types:
        votes_total = getter.get_votes_count(user, title_type)
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
            (cookie, user, friend_query, title_type, page)
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
    logger.info("Fetching info about titles [2/3]...")
    details = _get_details(ids, pool)
    logger.info("Fetching global rating for titles [3/3]...")
    global_rating = tuple(
        json.loads(el)
        for el in tqdm.tqdm(
            pool.imap_unordered(getter.get_global_rating, ids), total=total_titles
        )
    )
    return user, parser.merge_data(ids, [user_ratings, details, global_rating])


def main():
    args = docopt(__doc__)
    if args["--debug"]:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    workers = parser.resolve_workers(args["--workers"], CPU_COUNT)
    pool = multiprocessing.Pool(processes=workers)
    try:
        formats = {f.lower() for f in (args["--format"] or ("json",))}
        write_stdout = args["--stdout"]
        if write_stdout:
            assert len(formats) == 1, (
                f"Only one format can be written to stdout, passed: {formats}"
            )
        if args["search"]:
            assert formats.issubset({"csv", "json"}), (
                "Search supports file formats: csv, json"
            )
            query, movies = search(args, pool)
            writer.write_search(movies, query, write_stdout, formats)
        elif args["details"]:
            assert formats.issubset({"csv", "json"}), (
                "Search supports file formats: csv, json"
            )
            movies = details(args, pool)
            writer.write_details(movies, write_stdout, formats)
        else:
            assert formats and formats.issubset({"csv", "json", "letterboxd"}), (
                f"Supported file formats: {supported_formats}"
            )
            user, movies = user_export(args, pool)
            writer.write_user_export(movies, user, write_stdout, formats)
    except Exception as e:  # noqa
        logger.error(f"Program error: {e!s}")
    finally:
        pool.close()


if __name__ == "__main__":
    main()
