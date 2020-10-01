import re
import time
import json
import requests
import urllib.parse
from bs4 import BeautifulSoup
from datetime import datetime

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
LISTS_MAPPING = {
    'directors': 'filmPreview__info--directors',
    'countries': 'filmPreview__info--countries',
    'genres': 'filmPreview__info--genres',
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
    # https://www.filmweb.pl/login?error=bad.credentials IF FAIL
    assert not bool(re.search('login.*credentials', response.url)), 'Bad credentials'
    return True

def get_page(session, user, n):
    """
    get page with films
    """
    url = f'https://www.filmweb.pl/user/{user}/films'
    params = {'page': n}
    content = session.get(url, params=params).text
    return content

def parse_page(content):
    """
    get page with films
    """
    soup = BeautifulSoup(content)
    user_data_container = soup.find('span', attrs={'data-source': 'userVotes'})
    raw_votes = tuple(json.loads(script.contents[0]) for script in user_data_container.find_all('script'))
    movies = []
    for movie in raw_votes:
        movie_id = movie.get('eId')
        film_info_container = soup.find('div', attrs={'id': f'filmPreview_{movie_id}'})
        film_data = {}
        for el in film_info_container.find_all():
            for key, data_attr in ATTRS_MAPPING.items():
                try:
                    film_data[key] = el[data_attr]
                except:
                    continue
        for key, css_class in LISTS_MAPPING.items():
            data_container = soup.find(re.compile('.*'), attrs={'class': css_class})
            data = tuple(el.text for el in data_container.find_all('li'))
            film_data[key] = data
        original_title = soup.find(re.compile('.*'), attrs={'class': 'filmPreview__originalTitle'}).contents[0]
        pl_title = soup.find(re.compile('.*'), attrs={'class': 'filmPreview__title'}).contents[0]
        link = soup.find(re.compile('.*'), attrs={'class': 'filmPreview__link'})['href']
        timestamp = movie.get('t')
        clean_movie = {
            **film_data,
            'timestamp': timestamp,
            'iso_date': datetime.fromtimestamp(timestamp).isoformat(),
            'user_vote': movie.get('r'),
            'original_title': original_title,
            'pl_title': pl_title,
            'link': link,
        }
        movies.append(clean_movie)
    return movies 

# https://www.filmweb.pl/logout

# session.cookies.clear()

# span blockHeader__titleInfoCount TOTAL

# 25 per page COUNT

# vote count
# int(soup.find('div', attrs={'class': 'userPreview'})['data-votes-count'])