import json
from datetime import datetime

import requests

HEADERS = {
    # https://www.whatismybrowser.com/guides/the-latest-user-agent/firefox
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:159.0) Gecko/20100101 Firefox/159.0",
    "Host": "www.filmweb.pl",
    "Referer": "https://www.filmweb.pl",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Origin": "https://www.filmweb.pl",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Sec-GPC": "1",
    "TE": "trailers",
    "x-locale": "pl-PL",
}


def get_titles_page(args):
    """
    request title page
    """
    # this workaround is necessary because multiprocessing imap takes one arg only
    (cookie, user, friend_query, title_type, n) = args
    if friend_query:
        url = f"https://www.filmweb.pl/api/v1/logged/friend/{user}/vote/title/{title_type}?page={n}"
    else:
        url = f"https://www.filmweb.pl/api/v1/logged/vote/title/{title_type}?page={n}"
    data = _get_json(url, cookie, "get_titles_page")
    for entry in data:
        entry["movie_id"] = entry.get("entity")
        entry["user_rating"] = entry.get("rate")
        entry["date"] = datetime.fromtimestamp(entry["timestamp"] / 1000).strftime(
            "%Y-%m-%d"
        )
    return json.dumps(data)


def auth_check(cookie):
    """
    Check if auth is OK (valid cookie after login)
    """
    url = "https://www.filmweb.pl/api/v1/logged/info"
    content = _get_json(url, cookie, "auth_check")
    user = content["name"]
    return user


def get_votes_count(user, title_type):
    """
    Get total count of user votes for one title type: https://www.filmweb.pl/api/v1/user/{user}/votes/{title_type}/count
        Args:
        user: user to get ratings for
        title_type: type of title to fetch
    """
    url = f"https://www.filmweb.pl/api/v1/user/{user}/votes/{title_type}/count"
    return _get_json(url, "", "get_votes_count")


def get_global_rating(title_id):
    """
    Get global rating for a title
    """
    url = f"https://www.filmweb.pl/api/v1/film/{title_id}/rating"
    data = _get_json(url, "", "get_global_rating")
    data["movie_id"] = title_id
    data["global_rating"] = data.get("rate")
    data["global_rating_count"] = data.get("count")
    data["global_rating_histogram"] = {
        rating: data.get(f"countVote{rating}") for rating in range(1, 11)
    }
    return json.dumps(data)


def get_preview(title_id):
    """
    Get info about a title
    """
    url = f"https://www.filmweb.pl/api/v1/film/{title_id}/preview"
    data = _get_json(url, "", "get_preview")
    data["movie_id"] = title_id
    return json.dumps(data)


def _get_json(url, cookie, func_name):
    """
    Wrapper for request and unified error
    """
    try:
        headers = {"Cookie": cookie, **HEADERS}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        content = response.json()
    except Exception as e:  # noqa
        raise ValueError(f"Failure in {func_name}: {e!s}")
    else:
        return content
