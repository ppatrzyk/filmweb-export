import requests

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0',
    'Host': 'www.filmweb.pl',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Origin': 'https://www.filmweb.pl',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

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

def get_profile_page(user):
    """
    Parse films page to extract total count of votes
    Args:
        user: user to get ratings for
    """
    url = f'https://www.filmweb.pl/user/{user}'
    response = requests.get(url, headers=HEADERS)
    try:
        response.raise_for_status()
    except Exception as e:
        raise ValueError(f'No user {user} found: {str(e)}')
    return response.text
