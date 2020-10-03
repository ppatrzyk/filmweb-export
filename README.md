# filmweb-export

Export ocen z serwisu [Filmweb](https://www.filmweb.pl).

## Instalacja

Wymagania:

- [Python](https://www.python.org/).

Instalacja:

```
pip install https://github.com/ppatrzyk/filmweb-export/archive/master.zip
```

## Instrukcja

Filmweb wymaga zalogowania, aby uzyskać dostęp do wszystkich ocen. Istnieje możliwość eksportu własnych ocen, np.:

```
$ filmweb <LOGIN> <HASŁO>
INFO:root:Fetching data...
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 31/31 [00:06<00:00,  5.13it/s]
INFO:root:Parsing data...
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 31/31 [00:06<00:00,  4.52it/s]
INFO:root:pieca_filmweb_20201003.csv written!
$ head -3 pieca_filmweb_20201003.csv 
"duration_min","year","global_votes","global_rating","directors","countries","genres","timestamp","iso_date","user_vote","original_title","pl_title","link"
"105","2013-03-15","19006","7.108230113983154","['Sławomir Fabicki']","['Polska']","['Dramat obyczajowy']","1594412058","2020-07-10T22:14:18","9","","Miłość","https://www.filmweb.pl/film/Mi%C5%82o%C5%9B%C4%87-2012-631551"
"113","2017-09-22","5418","5.435029983520508","['Krzysztof Krauze']","['Polska']","['Dramat społeczny']","1594304693","2020-07-09T16:24:53","7","","Ptaki śpiewają w Kigali","https://www.filmweb.pl/film/Ptaki+%C5%9Bpiewaj%C4%85+w+Kigali-2017-595615"
```

lub ocen innego użytkownika (musi być znajomym logującego się):

```
$ filmweb <LOGIN> <HASŁO> -u <LOGIN_ZNAJOMEGO>
(...)
```

Wszystkie opcje:

```
$ filmweb -h
filmweb

Usage:
    filmweb <username> <password> [--format=<fileformat>] [--get_user=<username>] [--debug]

Options:
    -h --help                     Show this screen
    -f --format=<fileformat>      Output file format: csv (default) or json
    -u --get_user=<username>      User whose ratings are fetched (default: user logging in)
    -d --debug                    Debug prints
```

## Dostępne dane:

- duration_min: _długość w min_
- year: _premiera_
- global_votes: _ilość ocen filmu_
- global_rating: _ocena filmweb_
- directors: _reżyserzy (lista)_
- countries: _kraje (lista)_
- genres: _gatunki (lista)_
- timestamp: _[czas oceny (unix)](https://pl.wikipedia.org/wiki/Czas_uniksowy)_
- iso_date: _[czas oceny (ISO)](https://pl.wikipedia.org/wiki/ISO_8601)_
- user_vote: _ocena użytkownika_
- original_title: _tytuł oryginalny_
- pl_title: _tytuł polski_
- link: _strona filmu_

## Znane ograniczenia:

- Logowanie tylko kontem filmweb,
- Eksport tylko ocen filmów, inne (np. seriale) niedostępne,
