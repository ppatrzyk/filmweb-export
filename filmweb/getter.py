import requests

HEADERS = {
    # https://www.whatismybrowser.com/guides/the-latest-user-agent/firefox
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 13.1; rv:109.0) Gecko/20100101 Firefox/109.0',
    'x-locale': 'pl_PL',
    'Host': 'www.filmweb.pl',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Origin': 'https://www.filmweb.pl',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

def auth_check(cookie):
    """
    Check if auth is OK (valid cookie after login)
    """
    url = "https://www.filmweb.pl/api/v1/logged/info"
    try:
        response = requests.get(url, headers={'Cookie': cookie, **HEADERS})
        response.raise_for_status()
        content = response.json()
        user = content["name"]
    except Exception as e:
        raise ValueError(f'Auth failure: {str(e)}')
    else:
        return user

def get_films_page(args):
    """
    request films page
    """
    # this workaround is necessary because multiprocessing imap takes one arg only
    (cookie, user, n) = args
    url = f'https://www.filmweb.pl/user/{user}/films'
    params = {'page': n}
    response = requests.get(url, params=params, headers={'Cookie': cookie, **HEADERS})
    response.raise_for_status()
    return response.text

def get_votes_count(user):
    """
    Get total count of votes
    Args:
        user: user to get ratings for
    """
    url = f'https://www.filmweb.pl/api/v1/user/{user}/votes/film/count'
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        assert response.text, "Empty response for user vote count"
        count = int(response.text)
    except Exception as e:
        raise ValueError(f'No user {user} found: {str(e)}')
    return count

def get_user_rating(args):
    """
    Gets user rating
    """
    (cookie, movie_id, user, friend_query) = args
    if friend_query:
        url = f"https://www.filmweb.pl/api/v1/logged/friend/{user}/vote/film/{movie_id}/details"
    else:
        url = f"https://www.filmweb.pl/api/v1/logged/vote/film/{movie_id}/details"
    try:
        response = requests.get(url, headers={'Cookie': cookie, **HEADERS})
        response.raise_for_status()
        content = response.json()
    except Exception as e:
        raise ValueError(f'Failure in get_user_rating: {str(e)}')
    else:
        return content

def get_global_info(movie_id):
    """
    """
    url = f"https://www.filmweb.pl/api/v1/title/{movie_id}/info"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        content = response.json()
    except Exception as e:
        raise ValueError(f'Failure in get_global_info: {str(e)}')
    else:
        return content

def get_global_rating(movie_id):
    """
    """
    url = f"https://www.filmweb.pl/api/v1/title/{movie_id}/info"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        content = response.json()
    except Exception as e:
        raise ValueError(f'Failure in get_global_rating: {str(e)}')
    else:
        return content
