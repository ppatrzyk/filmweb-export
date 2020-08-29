import hashlib
import urllib
import requests
from bs4 import BeautifulSoup

API_HOST = 'https://ssl.filmweb.pl/api'
API_VERSION = '1.0'
API_ID = 'android'
API_KEY = 'qjcGhW2JnvGT9dfCt3uT_jozR3s'

def get_user_id(user_name):
    """
    Check user ID based on user name
    """
    fw_url = f'https://www.filmweb.pl/user/{user_name}'
    try:
        fw_page = requests.get(fw_url)
    except Exception as e:
        raise ValueError(f'Connection to filmweb.pl failed: {str(e)}')
    try:
        soup = BeautifulSoup(fw_page.content, "html.parser")
        fw_preview = soup.find('div', class_='userPreview')
        fw_uid = fw_preview['data-id']
    except Exception as e:
        raise ValueError(f'Error parsing profile page: {str(e)}')
    assert fw_uid != '$user.id', f'user {user_name} does not exist'
    return fw_uid

def get_params():
    """
    Format request parameters
    """
    params = {
        'version': API_VERSION,
        'appId': API_ID,
        'methods': None,
        'signature': None
    }
    return params