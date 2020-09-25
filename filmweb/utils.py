import hashlib
import urllib
import requests
from bs4 import BeautifulSoup

API_HOST = 'https://ssl.filmweb.pl/api'
API_VERSION = '1.0'
API_ID = 'android'
API_KEY = 'qjcGhW2JnvGT9dfCt3uT_jozR3s'
HEADERS = {'User-Agent': 'None'}

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

def get_params(method, method_params):
    """
    Format request parameters
    """
    method = f'{method} {str(list(method_params))}\n'
    signature = f'{method}{API_ID}{API_KEY}'
    md5 = hashlib.md5()
    md5.update(signature.encode('utf-8'))
    signature = f'{API_VERSION},{md5.hexdigest()}'
    params = {
        'version': urllib.parse.quote(API_VERSION),
        'appId': urllib.parse.quote(API_ID),
        'methods': urllib.parse.quote(method),
        'signature': signature,
    }
    return params

def login(user, password):
    """
    """
    params = get_params('login', [user, password, 1])
    return params

def get_user_ratings(user_id):
    """
    """
    params = get_params('getUserFilmVotes', [user_id, -1])
    return params

def call_api(session, params, method='get'):
    kwargs = {'url': API_HOST, 'params': params, 'headers': HEADERS}
    print(kwargs)
    if method == 'get':
        response = session.get(**kwargs)
    elif method == 'post':
        response = session.post(**kwargs)
    else:
        raise ValueError(f'Invalid method {method}')
    assert response.status_code == 200, 'Server error'
    print(response.text)

# TODO implement remaining methods
# if not logged in UserNotLoggedInException regex check
# session.cookies.clear() at the end
# ^err on invalid, ^ok on valid ^exc on exception