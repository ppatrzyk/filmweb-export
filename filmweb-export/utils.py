import requests
from bs4 import BeautifulSoup

def get_user_id(user_name):
    """
    Check user ID based on user name
    """
    fw_url = f'https://www.filmweb.pl/user/{user_name}'
    try:
        fw_page = requests.get(fw_url)
    except Exception as e:
        raise ValueError(f'Connection to filmweb.pl failed: {str(e)}')
    soup = BeautifulSoup(fw_page.content, "html.parser")
    fw_preview = soup.find('div', class_='userPreview')
    fw_uid = fw_preview['data-id']
    assert fw_uid != '$user.id', f'user {user_name} does not exist'
    return fw_uid

print(get_user_id('pieca'))