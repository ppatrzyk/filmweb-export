import re
import time
import csv
import json
import logging
import itertools
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
CSV_ROWS = (
    'timestamp',
    'iso_date',
    'user_comment',
    'user_vote',
    'global_rating',
    'global_votes',
    'original_title',
    'pl_title',
    'directors',
    'countries',
    'genres',
    'link',
    'duration_min',
    'year',
)

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
    logging.debug(f'Login done, reached: {response.url}')
    response.raise_for_status()
    # https://www.filmweb.pl/login?error=bad.credentials IF FAIL
    assert not bool(re.search('login.*error', response.url)), 'Login failed'
    return True

def logout(session):
    """
    Logout user
    """
    session.get('https://www.filmweb.pl/logout', headers=HEADERS)
    return True

def get_user_id(session, user):
    """
    Gets user id (necessary for friendship check)
    """
    url = f'https://www.filmweb.pl/user/{user}'
    response = session.get(url, headers=HEADERS)
    response.raise_for_status()
    logging.debug(f'Id check, reached {response.url}')
    assert response.url == url, f'User {user} does not exist'
    soup = BeautifulSoup(response.text, 'html.parser')
    user_id = soup.find('div', attrs={'class': 'userPreview'})['data-id']
    return user_id

def get_page(args):
    """
    request films page
    """
    # this workaround is necessary because multiprocessing imap takes one arg only
    (session, user, n) = args
    url = f'https://www.filmweb.pl/user/{user}/films'
    params = {'page': n}
    response = session.get(url, params=params, headers=HEADERS)
    response.raise_for_status()
    return response.text

def get_vote_count(session, user, friend_check=None):
    """
    Parse films page to extract total count of votes
    Args:
        session: requests session
        user: user to get ratings for
        friend_check: None when getting for logging in
            otherwise need to check if the user has us in friends 
    """
    url = f'https://www.filmweb.pl/user/{user}'
    response = session.get(url, headers=HEADERS)
    try:
        response.raise_for_status()
    except Exception as e:
        raise ValueError(f'No user {user} found: {str(e)}')
    soup = BeautifulSoup(response.text, 'html.parser')
    if friend_check:
        try:
            friends_ids = soup.find('div', attrs={'class': 'userPreview'})['data-friends-ids']
        except Exception as e:
            raise ValueError(f'User {user} has no friends: {str(e)}')
        assert bool(re.search(friend_check, friends_ids)), f'No access, user {user} is not a friend'
    try:
        # TODO? future: other types than films are counted here as well 
        user_info_container = soup.find('div', attrs={'class': 'voteStatsBoxData'})
        user_info = json.loads(user_info_container.text)
        ratings = user_info.get('votes').get('films')
    except Exception as e:
        raise ValueError(f'No ratings count found on website: {str(e)}')
    ratings = int(ratings)
    assert ratings > 0, 'no rating data available'
    return ratings

def get_movie_ratings(content):
    """
    Parse films page to extract movie ratings
    Args:
        content: raw html
    """
    soup = BeautifulSoup(content, 'html.parser')
    user_data_container = soup.find('span', attrs={'data-source': 'userVotes'})
    raw_votes = tuple(json.loads(script.contents[0]) for script in user_data_container.find_all('script'))
    movies = []
    for movie in raw_votes:
        movie_id = movie.get('eId')
        film_info_container = soup.find('div', attrs={'id': f'filmPreview_{movie_id}'})
        assert film_info_container, f'no container for {movie}'
        film_data = {}
        for el in film_info_container.find_all():
            for key, data_attr in ATTRS_MAPPING.items():
                try:
                    film_data[key] = el[data_attr]
                except:
                    continue
        for key, css_class in LISTS_MAPPING.items():
            data_container = film_info_container.find(re.compile('.*'), attrs={'class': css_class})
            try:
                data = tuple(el.text for el in data_container.find_all('li'))
            except:
                data = tuple()
            film_data[key] = data
        try:
            film_data['original_title'] = film_info_container.find(re.compile('.*'), attrs={'class': 'filmPreview__originalTitle'}).contents[0]
        except:
            pass
        try:
            film_data['pl_title'] = film_info_container.find(re.compile('.*'), attrs={'class': 'filmPreview__title'}).contents[0]
        except:
            pass
        try:
            film_data['link'] = 'https://www.filmweb.pl' + film_info_container.find(re.compile('.*'), attrs={'class': 'filmPreview__link'})['href']
        except:
            pass
        timestamp = movie.get('t')
        clean_movie = {
            **film_data,
            'timestamp': timestamp,
            'iso_date': datetime.fromtimestamp(timestamp).isoformat(),
            'user_vote': movie.get('r'),
            'user_comment': movie.get('c'),
        }
        movies.append(clean_movie)
    # necessary for multiprocessing pickle to work
    movies = json.dumps(movies)
    return movies

def write_data(movies, user, data_format='json'):
    """
    """
    assert movies, 'no data to write'
    date = datetime.now().strftime('%Y%m%d')
    movies_clean = itertools.chain.from_iterable((json.loads(el) for el in movies))
    movies_clean = tuple(movies_clean)
    if data_format == 'all':
        file_formats = ('csv', 'json')
    else:
        file_formats = (data_format, )
    if 'json' in file_formats:
        file_name = f'{user}_filmweb_{date}.json'
        with open(file_name, 'w', encoding='utf-8') as out_file:
            out_file.write(json.dumps(movies_clean))
        logging.info(f'{file_name} written!')
    if 'csv' in file_formats:
        file_name = f'{user}_filmweb_{date}.csv'
        with open(file_name, 'w', encoding='utf-8') as out_file:
            writer = csv.DictWriter(out_file, fieldnames=CSV_ROWS, dialect='unix')
            writer.writeheader()
            for movie in movies_clean:
                writer.writerow(movie)
        logging.info(f'{file_name} written!')
    return file_name
