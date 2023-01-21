import csv
import logging
import json
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

KEY_MAPPING = {
    'timestamp': 'timestamp',
    'favorite': 'favorite',
    'rate': 'user_rating',
    'global_rate': 'global_rating',
    'count': 'global_rating_count',
    'originalTitle': 'original_title',
    'title': 'pl_title',
    'year': 'year',
    'movie_id': 'movie_id',
    'url': 'url',
}

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

def merge_data(ids, user_ratings, global_info, global_rating):
    """
    Merge all data into one
    """
    all_data = tuple(_movie_id_key(el) for el in (user_ratings, global_info, global_rating))
    merged = ({**all_data[0][id], **all_data[1][id], **all_data[2][id]} for id in ids)
    return tuple(_rewrite_keys(entry) for entry in merged)

def _movie_id_key(data):
    """
    Reformat data into dict with movie_id as key
    """
    data = (json.loads(el) for el in data)
    return {entry["movie_id"]: entry for entry in data}

def _rewrite_keys(entry):
    """
    Fix keys names for data
    """
    fixed = {new_key: entry.get(old_key) for old_key, new_key in KEY_MAPPING.items()}
    if fixed.get("original_title") is None:
        fixed["original_title"] = fixed["pl_title"]
    path = quote_plus(f"{fixed['pl_title'].strip()}-{fixed['year']}-{fixed['movie_id']}")
    fixed["url"] = f"https://www.filmweb.pl/film/{path}"
    return fixed

def write_data(movies, user, data_format='json'):
    """
    """
    assert movies, 'no data to write'
    date = datetime.now().strftime('%Y%m%d')
    if data_format == 'all':
        file_formats = ('csv', 'json')
    else:
        file_formats = (data_format, )
    if 'json' in file_formats:
        file_name = f'{user}_filmweb_{date}.json'
        with open(file_name, 'w', encoding='utf-8') as out_file:
            out_file.write(json.dumps(movies))
        logging.info(f'{file_name} written!')
    if 'csv' in file_formats:
        file_name = f'{user}_filmweb_{date}.csv'
        with open(file_name, 'w', encoding='utf-8') as out_file:
            writer = csv.DictWriter(out_file, fieldnames=KEY_MAPPING.values(), dialect='unix')
            writer.writeheader()
            for movie in movies:
                writer.writerow(movie)
        logging.info(f'{file_name} written!')
    return file_name
