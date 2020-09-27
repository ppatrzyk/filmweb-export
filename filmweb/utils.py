import re
import time
import json
import requests
import urllib.parse
from bs4 import BeautifulSoup

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
LOGIN_POST_DATA = {
    'login_redirect_url': 'https://ssl.filmweb.pl/',
    '_prm': 'true',
}
ATTRS_MAPPING = {
    'global_votes': 'data-count',
    'global_rating': 'data-rate',
    'duration_min': 'data-duration',
    'year': 'data-release',
}

def login(session, user, password):
    """
    Login
    """
    params = {
        'j_username': user,
        'j_password': password,
        **LOGIN_POST_DATA
    }
    post_headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': 'https://www.filmweb.pl/login',
        'Cookie': f'canProfile=true_{int(time.time())}',
        **HEADERS
    }
    response = session.post(
        url='https://www.filmweb.pl/j_login',
        data=urllib.parse.urlencode(params),
        headers=post_headers,
    )
    response.raise_for_status()
    assert not bool(re.search('login.*credentials', response.url)), 'Bad credentials'
    return True

def get_page(n):
    """
    get page with films
    """
    # TODO requedt
    user_data_container = soup.find('span', attrs={'data-source': 'userVotes'})
    raw_votes = tuple(json.loads(script.contents[0]) for script in user_data_container.find_all('script'))
    # TODO for each vote
    film_info_container = soup.find('div', attrs={'id': 'filmPreview_IDHERE'})
    film_data = {}
    for el in film_info_container.find_all():
        for key, data_attr in ATTRS_MAPPING.items():
            try:
                film_data[key] = el[data_attr]
            except:
                continue



# TODO strategy 2
# POST https://www.filmweb.pl/j_login
# j_username=USER&j_password=PASS&_login_redirect_url=https%253A%252F%252Fssl.filmweb.pl%252F&_prm=true
# https://www.filmweb.pl/user/USER/films?page=4

# POST /j_login HTTP/1.1
# 'Content-Type': 'application/x-www-form-urlencoded'
# 'Referer': 'https://www.filmweb.pl/login'
#      otherwise https://www.filmweb.pl/user/USER/films

# login https://www.filmweb.pl/login?error=bad.credentials IF FAIL, otherwise /films

# https://www.filmweb.pl/logout

# session.cookies.clear()

# span blockHeader__titleInfoCount TOTAL

# 25 per page COUNT