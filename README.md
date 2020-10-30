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
$ filmweb <LOGIN> <HASŁO>
INFO:root:Fetching data...
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 31/31 [00:06<00:00,  5.13it/s]
INFO:root:Parsing data...
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 31/31 [00:06<00:00,  4.52it/s]
INFO:root:pieca_filmweb_20201030.csv written!
$ head -6 pieca_filmweb_20201030.csv
"timestamp","iso_date","user_comment","user_vote","global_rating","global_votes","original_title","pl_title","directors","countries","genres","link","duration_min","year"
"1570914666","2019-10-12T23:11:06","","7","6.438159942626953","3590","Play","Gra","['Ruben Östlund']","['Dania', 'Francja', 'Szwecja']","['Dramat', 'Akcja']","https://www.filmweb.pl/film/Gra-2011-508918","118","2011-11-11"
"1570914495","2019-10-12T23:08:15","","4","7.019690036773682","14935","Kraftidioten","Obywatel roku","['Hans Petter Moland']","['Norwegia', 'Szwecja']","['Komedia kryminalna']","https://www.filmweb.pl/film/Obywatel+roku-2014-684846","116","2014-05-16"
"1588403409","2020-05-02T09:10:09","","8","6.9715399742126465","773","Slava","Sława","['Kristina Grozeva']","['Grecja', 'Bułgaria']","['Dramat']","https://www.filmweb.pl/film/S%C5%82awa-2016-769511","101","2017-08-25"
"1570477126","2019-10-07T21:38:46","","5","6.0","4","","Důvěrný nepřítel","[]","['Czechy', 'Słowacja']","['Thriller']","https://www.filmweb.pl/film/D%C5%AFv%C4%9Brn%C3%BD+nep%C5%99%C3%ADtel-2018-819208","","2018-08-16"
"1570272939","2019-10-05T12:55:39","","6","6.264530181884766","5557","","Attenberg","['Athina Rachel Tsangari']","['Grecja']","['Dramat']","https://www.filmweb.pl/film/Attenberg-2010-591326","95","2011-11-25"
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
