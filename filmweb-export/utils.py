import requests
from bs4 import BeautifulSoup

user_name = 'pieca'

fw_url = 'https://www.filmweb.pl/user/{}'.format(user_name)
try:
    fw_page = requests.get(fw_url)
except Exception as e:
    pass
soup = BeautifulSoup(fw_page.content, "html.parser")
fw_preview = soup.find('div', class_='userPreview')
try:
    fw_uid = fw_preview['data-id']
    assert fw_uid != '$user.id'
except Exception as e:
    pass

print(fw_uid)