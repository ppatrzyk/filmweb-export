import csv
import json
import logging
from datetime import datetime
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)

TITLE_TYPE_OUTPUT_MAPPING = {"film": "movie", "serial": "tv_show", "videogame": "game"}
DETAILS_KEYS = (
    "movie_id",
    "duration",
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
    "global_rating",
    "global_rating_count",
    "global_rating_histogram",
)
USER_EXPORT_KEYS = DETAILS_KEYS + (
    "timestamp",
    "favorite",
    "user_rating",
)
POSTER_URL_PREFIX = "https://fwcdn.pl/fpo"
POSTER_SIZE = 10  # size used by filmweb in the list of ratings


def parse_details(entry):
    """
    Parse response of film preview api into title info
    """
    fixed = {
        "movie_id": entry.get("movie_id"),
        "duration": entry.get("duration"),
        "poster_url": _poster_url(entry.get("poster", {}).get("path")),
        "pl_title": entry.get("title", {}).get("title"),
        "original_title": entry.get("originalTitle", {}).get("title"),
        "year": entry.get("year"),
        "title_type": entry.get("entityName"),
        "title_sub_type": entry.get("subType"),
        "plot": entry.get("plotOrDescriptionSynopsis"),
        "genres": [
            genre.get("name", {}).get("text") for genre in entry.get("genres", [])
        ],
        "directors": [director.get("name") for director in entry.get("directors", [])],
        "countries": [country.get("code") for country in entry.get("countries", [])],
    }
    fixed["title_type"] = TITLE_TYPE_OUTPUT_MAPPING.get(
        fixed.get("title_type"), fixed.get("title_type")
    )
    if fixed.get("pl_title") is None:
        fixed["pl_title"] = fixed.get("original_title")
    if fixed.get("original_title") is None:
        fixed["original_title"] = fixed["pl_title"]
    path = quote_plus(
        f"""{(fixed["pl_title"] or "").strip()}-{fixed["year"]}-{fixed["movie_id"]}"""
    )
    fixed["url"] = f"https://www.filmweb.pl/film/{path}"
    return fixed


def _movie_id_key(data):
    """
    Parse and reformat data into dict with movie_id as key
    """
    return {entry["movie_id"]: entry for entry in data}


def merge_data(ids, data):
    """
    Merge all data into one
    """
    dicts = tuple(_movie_id_key(el) for el in data)
    merged = ({**d.get(movie_id, {}) for d in dicts} for movie_id in ids)
    return merged


def _poster_url(path):
    """
    Build url of poster image from api path, e.g.
    /39/15/643915/7889447_1.$.jpg -> https://fwcdn.pl/fpo/39/15/643915/7889447_1.10.webp
    """
    if not path:
        return None
    base = path.rpartition(".")[0]
    return f"{POSTER_URL_PREFIX}{base.replace('$', str(POSTER_SIZE))}.webp"


def _write_csv(file_name, field_names, movies):
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
    with open(file_name, "w", encoding="utf-8") as out_file:
        writer = csv.DictWriter(out_file, fieldnames=field_names, dialect="unix")
        writer.writeheader()
        for movie in movies_fixed:
            writer.writerow(movie)
    return True


def _letterbox_entry(entry):
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


def _write_data(movies, keys, file_name, formats):
    """Write export data to requested output formats"""
    assert movies, "no data to write"
    movies = [{k: v for k, v in m.items() if k in keys} for m in movies]
    written_files = []
    if "json" in formats:
        file = f"{file_name}.json"
        with open(file, "w", encoding="utf-8") as out_file:
            out_file.write(json.dumps(movies))
        logger.info(f"{file} written!")
        written_files.append(file)
    if "csv" in formats:
        file = f"{file_name}.csv"
        _write_csv(file, keys, movies)
        logger.info(f"{file} written!")
        written_files.append(file)
    if "letterboxd" in formats:
        file = f"{file_name}_letterboxd.csv"
        movies_letterbox = tuple(_letterbox_entry(entry) for entry in movies)
        _write_csv(file, movies_letterbox[0].keys(), movies_letterbox)
        logger.info(f"{file} written!")
        written_files.append(file)
    return tuple(written_files)


def write_details(movies, formats):
    date = datetime.now().strftime("%Y%m%d")
    file_name = f"details_{date}"
    return _write_data(movies, DETAILS_KEYS, file_name, formats)


def write_user_export(movies, user, formats):
    date = datetime.now().strftime("%Y%m%d")
    file_name = f"{user}_{date}"
    return _write_data(movies, USER_EXPORT_KEYS, file_name, formats)
