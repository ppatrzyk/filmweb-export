import json
import requests

HEADERS = {
    # https://www.whatismybrowser.com/guides/the-latest-user-agent/firefox
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:144.0) Gecko/20100101 Firefox/144.0",
    "x-locale": "pl_PL",
    "Host": "www.filmweb.pl",
    "Referer": "https://www.filmweb.pl",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Origin": "https://www.filmweb.pl",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": 'empty',
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Sec-GPC": "1",
    "TE": "trailers",
}

def get_films_page(args):
    """
    request films page
    """
    # this workaround is necessary because multiprocessing imap takes one arg only
    (cookie, user, friend_query, n) = args
    if friend_query:
        url = f"https://www.filmweb.pl/api/v1/logged/friend/{user}/vote/title/film?page={n}"
    else:
        url = f"https://www.filmweb.pl/api/v1/logged/vote/title/film?page={n}"
    data = _get_json(url, cookie, "get_films_page")
    return json.dumps(data)

def auth_check(cookie):
    """
    Check if auth is OK (valid cookie after login)
    """
    url = "https://www.filmweb.pl/api/v1/logged/info"
    content = _get_json(url, cookie, "auth_check")
    user = content["name"]
    return user

def get_votes_count(user):
    """
    Get total count of voteshttps://www.filmweb.pl/api/v1/user/{user}/votes/film/count
    Args:
        user: user to get ratings for
    """
    url = f"https://www.filmweb.pl/api/v1/user/{user}/votes/film/count"
    return _get_json(url, "", "get_votes_count")

def get_global_info(movie_id):
    """
    Get info about a movie (title etc)
    """
    url = f"https://www.filmweb.pl/api/v1/title/{movie_id}/info"
    data = _get_json(url, "", "get_global_info")
    data["entity"] = movie_id
    return json.dumps(data)

def get_global_rating(movie_id):
    """
    Get global rating for a movie
    """
    url = f"https://www.filmweb.pl/api/v1/film/{movie_id}/rating"
    data = _get_json(url, "", "get_global_rating")
    data["entity"] = movie_id
    data["global_rate"] = data.pop("rate")
    return json.dumps(data)

def _get_json(url, cookie, func_name):
    """
    Wrapper for request and unified error
    """
    try:
        response = requests.get(url, headers={"Cookie": cookie, **HEADERS})
        response.raise_for_status()
        content = response.json()
    except Exception as e:
        raise ValueError(f"Failure in {func_name}: {str(e)}")
    else:
        return content