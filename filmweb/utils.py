import requests
from bs4 import BeautifulSoup

HEADERS = {'User-Agent': 'None'}

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
