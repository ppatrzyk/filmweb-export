import requests
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0',
    'Host': 'www.filmweb.pl',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Origin': 'https://www.filmweb.pl',
    'DNT': 1,
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': 1,
}

# TODO strategy 2
# POST https://www.filmweb.pl/j_login
# j_username=USER&j_password=PASS&_login_redirect_url=https%253A%252F%252Fssl.filmweb.pl%252F&_prm=true
# https://www.filmweb.pl/user/USER/films?page=4

# POST /j_login HTTP/1.1
# 'Content-Type': 'application/x-www-form-urlencoded'
# 'Referer': 'https://www.filmweb.pl/login'
#      otherwise https://www.filmweb.pl/user/USER/films
