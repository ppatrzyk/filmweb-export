import csv
import json
import logging
import re
import sys
from contextlib import nullcontext
from datetime import datetime

logger = logging.getLogger(__name__)

DETAILS_KEYS = (
    "movie_id",
    "duration",
    "url",
    "poster_url",
    "pl_title",
    "original_title",
    "year",
    "title_type",
    "title_sub_type",
    "plot",
    "genres",
    "directors",
    "countries",
    "actors",
    "global_rating",
    "global_rating_count",
    "global_rating_histogram",
)
USER_EXPORT_KEYS = DETAILS_KEYS + (
    "timestamp",
    "favorite",
    "user_rating",
)
SEARCH_KEYS = (
    "movie_id",
    "type",
    "matched_title",
    "matched_lang",
    "actors",
)


def _letterbox_entry(entry: dict) -> dict:
    """
    Format letterboxd column names
    https://letterboxd.com/about/importing-data/
    """
    fixed = {
        "Title": entry.get("original_title"),
        "Year": entry.get("year"),
        "Rating10": entry.get("user_rating"),
        "WatchedDate": entry.get("date"),
    }
    return fixed


def _write_csv(file: str | None, field_names: tuple[str], movies: tuple[dict]) -> bool:
    """
    Helper for writing csv
    """
    movies_fixed = [
        {
            k: (json.dumps(v) if isinstance(v, (list, dict)) else v)
            for k, v in movie.items()
        }
        for movie in movies
    ]
    with open(file, "w") if file is not None else nullcontext(sys.stdout) as out_file:
        writer = csv.DictWriter(out_file, fieldnames=field_names, dialect="unix")
        writer.writeheader()
        for movie in movies_fixed:
            writer.writerow(movie)
    if file is not None:
        logger.info(f"{file} written!")
    return True


def _write_data(
    movies: tuple[dict], keys: tuple[str], file_name: str | None, formats: set[str]
) -> bool:
    """Write export data to requested output formats"""
    assert movies, "no data to write"
    logger.info("Writing data...")
    movies = [{k: v for k, v in m.items() if k in keys} for m in movies]
    if "json" in formats:
        raw_data = json.dumps(movies)
        if file_name is None:
            sys.stdout.write(raw_data)
        else:
            file = f"{file_name}.json"
            with open(file, "w", encoding="utf-8") as out_file:
                out_file.write(raw_data)
            logger.info(f"{file} written!")
    if "csv" in formats:
        file = f"{file_name}.csv" if file_name else file_name
        _write_csv(file, keys, movies)
    if "letterboxd" in formats:
        file = f"{file_name}_letterboxd.csv" if file_name else file_name
        movies_letterbox = tuple(_letterbox_entry(entry) for entry in movies)
        _write_csv(file, movies_letterbox[0].keys(), movies_letterbox)
    return True


def write_details(movies: tuple[dict], write_stdout: bool, formats: set) -> bool:
    file_name = None
    if not write_stdout:
        date = datetime.now().strftime("%Y%m%d")
        file_name = f"details_{date}"
    return _write_data(movies, DETAILS_KEYS, file_name, formats)


def write_search(
    movies: tuple[dict],
    query: str,
    write_stdout: bool,
    formats: set[str],
    embed_images: bool = False,
) -> bool:
    file_name = None
    if not write_stdout:
        date = datetime.now().strftime("%Y%m%d")
        slug = re.sub(r"\W+", "_", query.lower()).strip("_")[:40] or "query"
        file_name = f"search_{slug}_{date}"
    return _write_data(movies, SEARCH_KEYS, file_name, formats)


def write_user_export(
    movies: tuple[dict], user: str, write_stdout: bool, formats: set[str]
) -> bool:
    file_name = None
    if not write_stdout:
        date = datetime.now().strftime("%Y%m%d")
        file_name = f"{user}_{date}"
    return _write_data(movies, USER_EXPORT_KEYS, file_name, formats)
