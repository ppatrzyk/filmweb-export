import csv
import logging
import json
from datetime import datetime
from bs4 import BeautifulSoup

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

def extract_movie_ids(content):
    """
    Extract movie ids from films page
    Args:
        content: raw html
    """
    soup = BeautifulSoup(content, 'html.parser')
    id_containers = soup.find_all('div', attrs={'data-film-id': True})
    ids = set(el['data-film-id'] for el in id_containers)
    # necessary for multiprocessing pickle to work
    return json.dumps(list(ids))

def write_data(movies, user, data_format='json'):
    """
    """
    assert movies, 'no data to write'
    date = datetime.now().strftime('%Y%m%d')
    # movies_clean = itertools.chain.from_iterable((json.loads(el) for el in movies))
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
