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

Istnieje możliwość eksportu własnych ocen lub ocen znajomych - proszę podać nazwę użytkownika jako `username`. Do dostępu jest potrzebne zalogowanie się na portal i podanie do skryptu wartości `cookie` dla strony filmweb. Podstawowe użycie:

```
filmweb <username> <cookie>
```

### Skąd wziąć cookie?

1. Otwórz *Network Monitor* w przeglądarce (`Ctrl+Shift+E` w Firefoxie),
2. Zaloguj się i wejdź na filmweb. Znajdź i wejdź w szczegóły obecnej strony,
3. Wejdź w zakładkę *Headers* > *Request Headers*,
4. Skopiuj wartość *Cookie* i podaj ją jako argument do skryptu.

![Browser Screenshot](browser_screen.jpg)

### Przykład

```
$ filmweb -f csv -f json pieca "didomi_token=(...)=="
INFO:root:Checking args...
INFO:root:Fetching list of movies [1/4]...
100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 10/10 [00:00<00:00, 13.94it/s]
INFO:root:User pieca has 939 movies...
INFO:root:Fetching info about movies [2/4]...
100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 939/939 [00:37<00:00, 25.19it/s]
INFO:root:Fetching global rating for movies [3/4]...
100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 939/939 [00:39<00:00, 23.70it/s]
INFO:root:Writing data [4/4]...
INFO:root:pieca_20231207.json written!
INFO:root:pieca_20231207.csv written!
$ cat pieca_20231207.json | jq .[0]
{
  "timestamp": 1579354599456,
  "favorite": null,
  "user_rating": 5,
  "global_rating": 6.03865,
  "global_rating_count": 414,
  "original_title": "Ejdeha Vared Mishavad!",
  "pl_title": "Wejście smoka!",
  "year": 2016,
  "movie_id": "757318",
  "url": "https://www.filmweb.pl/film/Wej%C5%9Bcie+smoka%21-2016-757318",
  "date": "2020-01-18"
}
$ cat pieca_20231207.csv | xsv sample 3 | xsv table
timestamp      favorite  user_rating  global_rating  global_rating_count  original_title           pl_title                    year  movie_id  url                                                                      date
1445174195445            4            7.12156        4212                 Bella                    Bella                       2006  294905    https://www.filmweb.pl/film/Bella-2006-294905                            2015-10-18
1425511762032            4            6.36319        42906                Veronika Decides to Die  Weronika postanawia umrzeć  2009  459178    https://www.filmweb.pl/film/Weronika+postanawia+umrze%C4%87-2009-459178  2015-03-05
1638617602312            3            8.62545        995071               The Green Mile           Zielona mila                1999  862       https://www.filmweb.pl/film/Zielona+mila-1999-862      
```

### Wszystkie opcje

```
$ filmweb -h
filmweb

Usage:
    filmweb [--format=<fileformat>]... [--debug] <username> <cookie>

Options:
    -h --help                     Show this screen
    -f --format=<fileformat>      Output file format: json (default), csv, letterboxd
    -d --debug                    Debug prints
```

## Dostępne dane:

Kolumna | Opis
--- | ---
year | _premiera_
global\_rating\_count | _ilość ocen filmu_
global\_rating | _ocena filmweb_
timestamp | _[czas oceny (unix)](https://pl.wikipedia.org/wiki/Czas_uniksowy)_
date | _data oceny_ (yyyy-mm-dd)
user\_rating | _ocena użytkownika_
favorite | _dodany do ulubionych_
original\_title | _tytuł oryginalny_
pl\_title | _tytuł polski_
movie\_id | _id filmu_ (filmweb)
url | _strona filmu_

## Znane problemy:

- Eksport tylko ocen filmów, inne (np. seriale) niedostępne,
