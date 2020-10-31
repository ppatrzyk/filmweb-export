# filmweb-export

Export ocen z serwisu [Filmweb](https://www.filmweb.pl).

## Instalacja

Wymagania:

- [Python](https://www.python.org/).

Instalacja:

```
pip install filmweb
```

Albo:

```
pip install https://github.com/ppatrzyk/filmweb-export/archive/master.zip
```

## Instrukcja

Filmweb wymaga zalogowania, aby uzyskać dostęp do wszystkich ocen. Istnieje możliwość eksportu własnych ocen, np.:

```
$ filmweb <LOGIN> <HASŁO> --format csv
INFO:root:Fetching data...
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 31/31 [00:06<00:00,  5.13it/s]
INFO:root:Parsing data...
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 31/31 [00:06<00:00,  4.52it/s]
INFO:root:pieca_filmweb_20201031.csv written!
$ head -6 pieca_filmweb_20201031.csv
"timestamp","iso_date","user_comment","user_vote","global_rating","global_votes","original_title","pl_title","directors","countries","genres","link","duration_min","year"
"1580143639","2020-01-27T17:47:19","","3","7.2103400230407715","73632","What We Do in the Shadows","Co robimy w ukryciu","['Jemaine Clement']","['Nowa Zelandia', 'USA']","['Horror', 'Komedia', 'Dokumentalizowany']","https://www.filmweb.pl/film/Co+robimy+w+ukryciu-2014-707286","86","2015-02-27"
"1580143596","2020-01-27T17:46:36","","1","7.762599945068359","76768","","Jojo Rabbit","['Taika Waititi']","['Czechy', 'Niemcy', 'Nowa Zelandia', 'USA']","['Dramat', 'Komedia', 'Wojenny']","https://www.filmweb.pl/film/Jojo+Rabbit-2019-817417","108","2020-01-24"
"1580033558","2020-01-26T11:12:38","","6","6.284679889678955","966","Quick","Seryjny morderca","['Mikael Håfström']","['Szwecja']","['Thriller']","https://www.filmweb.pl/film/Seryjny+morderca-2019-832513","132","2020-09-03"
"1579429860","2020-01-19T11:31:00","","7","6.661180019378662","425","","Difret","['Zeresenay Mehari']","['USA', 'Etiopia']","['Dramat']","https://www.filmweb.pl/film/Difret-2014-700409","99","2015-03-27"
"1579354699","2020-01-18T14:38:19","","5","7.180500030517578","4471","Dylda","Wysoka dziewczyna","['Kantemir Balagov']","['Rosja']","['Dramat']","https://www.filmweb.pl/film/Wysoka+dziewczyna-2019-829460","130","2019-10-11"
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
- user_comment: _komentarz użytkownika_
- original_title: _tytuł oryginalny_
- pl_title: _tytuł polski_
- link: _strona filmu_

## Znane problemy:

- Logowanie tylko kontem filmweb,
- Eksport tylko ocen filmów, inne (np. seriale) niedostępne,
