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
    response = requests.get(url, headers={'Cookie': cookie, **HEADERS})
    try:
        response.raise_for_status()
    except Exception as e:
        raise ValueError(f'Auth failure: {str(e)}')
    return True

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
    response = requests.get(url, headers=HEADERS)
    try:
        response.raise_for_status()
        assert response.text, "Empty response for user vote count"
        count = int(response.text)
    except Exception as e:
        raise ValueError(f'No user {user} found: {str(e)}')
    return count

# TODO
# user rating
# https://www.filmweb.pl/api/v1/logged/vote/film/4186/details
# https://www.filmweb.pl/api/v1/logged/friend/kajka23/vote/film/1157/details

# global info, global rating
# https://www.filmweb.pl/api/v1/title/876864/info
# https://www.filmweb.pl/api/v1/film/108121/rating