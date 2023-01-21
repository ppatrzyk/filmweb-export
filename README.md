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
$ filmweb -f all pieca "didomi_token=(...)=="
INFO:root:Checking args...
INFO:root:Fetching list of movies...
100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 38/38 [00:06<00:00,  6.26it/s]
INFO:root:Parsing list of movies...
100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 38/38 [00:02<00:00, 12.79it/s]
INFO:root:User pieca has 926 movies...
INFO:root:Fetching movie details...
INFO:root:Fetching user ratings [1/3]...
100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 926/926 [00:39<00:00, 23.49it/s]
INFO:root:Fetching info about movies [2/3]...
100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 926/926 [00:43<00:00, 21.22it/s]
INFO:root:Fetching global rating for movies [3/3]...
100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 926/926 [00:43<00:00, 21.36it/s]
INFO:root:Writing data...
INFO:root:pieca_filmweb_20230121.json written!
INFO:root:pieca_filmweb_20230121.csv written!
$ cat pieca_filmweb_20230121.json | jq .[0]
{
  "timestamp": 1657484863818,
  "favorite": false,
  "user_rating": 8,
  "global_rating": 7.36859,
  "global_rating_count": 1579,
  "original_title": "Tehran Taboo",
  "pl_title": "Teheran tabu",
  "year": 2017,
  "movie_id": "786978",
  "url": "https://www.filmweb.pl/film/Teheran+tabu-2017-786978"
}
$ cat pieca_filmweb_20230121.csv | xsv sample 5 | xsv table
timestamp      favorite  user_rating  global_rating  global_rating_count  original_title  pl_title       year  movie_id  url
1464302814850  False     4            6.91279        1743                 Pupendo         Pupendo        2003  103930    https://www.filmweb.pl/film/Pupendo-2003-103930
1581177494926  False     7            6.51905        210                  Dukhtar         Dukhtar        2014  727743    https://www.filmweb.pl/film/Dukhtar-2014-727743
1601716769499  False     8            7.59777        179                  Shah-re ziba    Piękne miasto  2004  155344    https://www.filmweb.pl/film/Pi%C4%99kne+miasto-2004-155344
1548505975360  False     8            7.12276        1784                 Geu-mul         W sieci        2016  766555    https://www.filmweb.pl/film/W+sieci-2016-766555
1638616845248  False     5            6.59127        115166               Ida             Ida            2013  546529    https://www.filmweb.pl/film/Ida-2013-546529
```

### Wszystkie opcje

```
$ filmweb -h
filmweb

Usage:
    filmweb [--format=<fileformat>] [--debug] <username> <cookie>

Options:
    -h --help                     Show this screen
    -f --format=<fileformat>      Output file format: json (default), csv, all (writes both)
    -d --debug                    Debug prints                 Debug prints
```

## Dostępne dane:

Kolumna | Opis
--- | ---
year | _premiera_
global\_rating\_count | _ilość ocen filmu_
global\_rating | _ocena filmweb_
timestamp | _[czas oceny (unix)](https://pl.wikipedia.org/wiki/Czas_uniksowy)_
user\_rating | _ocena użytkownika_
favorite | _dodany do ulubionych_
original\_title | _tytuł oryginalny_
pl\_title | _tytuł polski_
movie\_id | _id filmu_
url | _strona filmu_

## Znane problemy:

- Eksport tylko ocen filmów, inne (np. seriale) niedostępne,
