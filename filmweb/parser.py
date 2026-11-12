import logging
import re
from datetime import datetime
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)

POSTER_URL_PREFIX = "https://fwcdn.pl/fpo"
POSTER_SIZE = 10  # size used by filmweb in the list of ratings
DEFAULT_TITLE_TYPES = {"movie", "tv_show", "game"}
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
TITLE_TYPE_TO_API = {"movie": "film", "tv_show": "serial", "game": "videogame"}
TITLE_TYPE_OUTPUT_MAPPING = {"film": "movie", "serial": "tv_show", "videogame": "game"}


def _movie_id_key(data: list[dict]):
    """
    Parse and reformat data into dict with movie_id as key
    """
    return {entry["movie_id"]: entry for entry in data}


def _poster_url(path: str | None) -> str | None:
    """
    Build url of poster image from api path, e.g.
    /39/15/643915/7889447_1.$.jpg -> https://fwcdn.pl/fpo/39/15/643915/7889447_1.10.webp
    """
    if not path:
        return None
    base = path.rpartition(".")[0]
    return f"{POSTER_URL_PREFIX}{base.replace('$', str(POSTER_SIZE))}.webp"


def merge_data(ids: tuple[int], data: list[list[dict]]) -> tuple[dict]:
    """
    Merge all data into one
    """
    dicts = tuple(_movie_id_key(el) for el in data)
    merged = tuple({**d.get(movie_id, {}) for d in dicts} for movie_id in ids)
    return merged


def normalize_title_types(raw_types: list[str]) -> tuple[str]:
    """Normalize user title type values to supported API types"""
    if not raw_types:
        title_types = DEFAULT_TITLE_TYPES
    else:
        raw_types = [title_type.lower().strip() for title_type in raw_types]
        if "all" in raw_types:
            title_types = DEFAULT_TITLE_TYPES
        else:
            title_types = set()
            for title_type in raw_types:
                resolved = TITLE_TYPE_ALIASES.get(title_type, None)
                assert resolved is not None, f"Unsupported title type: {title_type}"
                title_types.add(resolved)
    return tuple(TITLE_TYPE_TO_API[t] for t in title_types)


def parse_details(entry: dict):
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


def parse_pages(raw_pages: str) -> tuple[int, int]:
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


def parse_since(raw_since: str) -> int:
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


def resolve_workers(raw_workers: str, default: int) -> int:
    """Number of parallel workers: CPU count by default"""
    if raw_workers is None:
        return default
    try:
        workers = int(raw_workers)
        assert workers >= 1, "--workers must be at least 1"
        if workers > default:
            logger.warning(f"--workers={workers} exceeds default CPU count ({default})")
        return workers
    except ValueError:
        raise AssertionError(f"--workers must be positive integer, got: {raw_workers}")


def parse_ids(raw_ids: list[str]) -> tuple[int]:
    """Parse title ids given to details command, drop duplicates, keep order"""
    for raw_id in raw_ids:
        assert raw_id.isdigit(), f"Title id must be a number, got: {raw_id}"
    return tuple(dict.fromkeys(int(raw_id) for raw_id in raw_ids))
