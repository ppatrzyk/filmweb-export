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
    try:
        soup = BeautifulSoup(fw_page.content, "html.parser")
        fw_preview = soup.find('div', class_='userPreview')
        fw_uid = fw_preview['data-id']
    except Exception as e:
        raise ValueError(f'Error parsing profile page: {str(e)}')
    assert fw_uid != '$user.id', f'user {user_name} does not exist'
    return fw_uid

### copied - redo

fw = Filmweb()
fw.login(name = fw_name, password = fw_password)

user_obj = User(fw, name = user, uid = fw_id)
raw_data = user_obj.get_film_votes()
for entry in raw_data:
    entry['film'] = entry['film'].uid

movie_obj = Film(fw, uid = entry.pop('film'))
movie = movie_obj.get_info()

if type(movie.get('url')) is str:
    movie['url'] = re.sub(
        r'(?<=web\.pl/film/).+?(?=/$)',
        lambda match: r'{}'.format(quote_plus(match.group(0))), re.sub('discussion$', '', movie.get('url'))
    )

dir_list = movie_obj.get_persons(role_type = 'Reżyser')
dir_list = [director for director in dir_list if director.get('role_extra_info') is None]
if dir_list:
    director = dir_list[0]['person'].get_info()
    if type(director.get('birth_place')) is str:
        director['birth_place'] = re.sub('\(obecn.*?\)', '', director.get('birth_place'))
else:
    director = {'name':None, 'sex':None, 'birth_place':None, 'birth_date':None, 'death_date':None}