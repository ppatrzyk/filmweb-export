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

# TODO strategy 2
# POST https://www.filmweb.pl/j_login
# j_username=USER&j_password=PASS&_login_redirect_url=https%253A%252F%252Fssl.filmweb.pl%252F&_prm=true
# https://www.filmweb.pl/user/USER/films?page=4

# POST /j_login HTTP/1.1
# Host: www.filmweb.pl
# User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0
# Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
# Accept-Language: en-US,en;q=0.5
# Accept-Encoding: gzip, deflate, br
# Content-Type: application/x-www-form-urlencoded
# Content-Length: 138
# Origin: https://www.filmweb.pl
# DNT: 1
# Connection: keep-alive
# Referer: https://www.filmweb.pl/login
# Upgrade-Insecure-Requests: 1
