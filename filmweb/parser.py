import re
import csv
import itertools
import logging
import json
from datetime import datetime
from math import ceil
from bs4 import BeautifulSoup

MOVIES_PER_PAGE = 25
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

def get_pages_count(content):
    """
    Parse profile page to extract pages count
    Args:
        content: raw html
    """
    soup = BeautifulSoup(content, 'html.parser')
    try:
        # TODO? future: other types than films are counted here as well 
        user_info_container = soup.find('div', attrs={'class': 'voteStatsBoxData'})
        user_info = json.loads(user_info_container.text)
        ratings = int(user_info.get('votes').get('films'))
    except Exception as e:
        raise ValueError(f'No ratings count found on website: {str(e)}')
    assert ratings > 0, 'no rating data available'
    pages = ceil(ratings/MOVIES_PER_PAGE)
    return pages

def auth_check(content):
    """
    Parse films page to check authorization
    Args:
        content: raw html
    """
    access_error = """
    Ratings for this user cannot be accessed.
    Either auth cookie is incorrect or this user is not your friend
    """
    soup = BeautifulSoup(content, 'html.parser')
    no_rating_access = soup.find('div', attrs={'class': 'userVotesPage__limitedView'})
    assert not no_rating_access, access_error
    return True

def extract_movie_ratings(content):
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
