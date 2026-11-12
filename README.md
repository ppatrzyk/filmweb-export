# filmweb-export

Eksport ocen filmów, seriali i gier z serwisu [Filmweb](https://www.filmweb.pl).

## Instalacja

### Pakiet Python

```bash
pip install filmweb

# master branch na githubie:
pip install https://github.com/ppatrzyk/filmweb-export/archive/master.zip
```

Wymaga instalacji [Pythona](https://www.python.org/).

### Docker

```bash
podman run \
    --rm \
    -v ./:/filmweb \
    ghcr.io/ppatrzyk/filmweb-export:v0.14 \
    filmweb <username> <cookie>
```

### Gotowe binarki

Samodzielny plik wykonywalny zbudowany przy użyciu [PyInstaller](https://pyinstaller.org) (Linux, MacOS, Windows).

Pobierz z zakładki [Releases](https://github.com/ppatrzyk/filmweb-export/releases).

## Instrukcja

### Dane użytkownika

Istnieje możliwość eksportu własnych ocen lub ocen znajomych - proszę podać nazwę użytkownika jako `username`. Do dostępu jest potrzebne zalogowanie się na portal i podanie do skryptu wartości `cookie` dla strony filmweb. Podstawowe użycie:

```bash
filmweb <username> <cookie>
```

### Dane o filmach

Ściągnij dane o filmach według ich _id_ (nie wymaga logowania):

```bash
filmweb <id>
```

### Ograniczanie obciążenia serwera

Domyślnie program używa tylu równoległych procesów, ile jest dostępnych CPU. Można to ograniczyć opcją `--workers`:

```bash
filmweb --workers 2 <username> <cookie>
```

Domyślnie pobierane są wszystkie strony z listą ocen (po 100 tytułów na stronę, osobno dla każdego typu). Opcja `--pages` pozwala pobrać tylko wybrany zakres:

```bash
filmweb --pages 2-5 <username> <cookie>   # strony 2-5
filmweb --pages 3 <username> <cookie>     # tylko strona 3
filmweb --pages 4- <username> <cookie>    # od strony 4 do końca
```

### Przyrostowy eksport

Opcja `--since YYYY-MM-DD` eksportuje tylko tytuły ocenione (lub ze zmienioną oceną) w podanym dniu lub później (dzień włącznie). Lista ocen jest nadal pobierana w całości, ale kosztowne zapytania o informacje i oceny globalne dotyczą wyłącznie wybranych tytułów, więc eksport od ostatniej daty trwa o wiele krócej:

```bash
filmweb --since 2026-10-19 <username> <cookie>
```

Dlaczego lista ocen jest pobierana w całości, a nie tylko do pierwszej starszej oceny? Filmweb zwraca oceny w stałej kolejności (domyślnie od najnowszej dodanej), ale pole `timestamp` to czas ostatniej zmiany oceny. Gdy zmienisz ocenę starego filmu, jego `timestamp` jest nowy, a pozycja na liście pozostaje zwykle na dawnym miejscu. Pobieranie od początku i przerwanie na pierwszej starej ocenie pominęłoby takie zmiany. Dodatkowo strony listy są pobierane równolegle, więc kolejność w pliku wynikowym nie jest chronologiczna.

### Skąd wziąć cookie?

 - [Network Monitor w przeglądarce](cookies_browser.md)
 - [Rozszerzenie cookie-editor](cookies_extension.md)

### Przykład

#### Dane użytkownika

```bash
$ filmweb -f csv -f json pieca "didomi_token=(...)=="
INFO:root:Checking args...
INFO:root:Fetching list of rated titles [1/4]...
INFO:root:Fetching list of movie ratings...
100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 10/10 [00:00<00:00, 43.70it/s]
INFO:root:Fetching list of tv_show ratings...
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 10.30it/s]
INFO:root:Skipping game, no ratings found
INFO:root:User pieca has 955 rated titles...
INFO:root:Fetching info about titles [2/4]...
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 955/955 [01:02<00:00, 15.21it/s]
INFO:root:Fetching global rating for titles [3/4]...
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 955/955 [01:15<00:00, 12.72it/s]
INFO:root:Writing data [4/4]...
INFO:root:pieca_20260604.json written!
INFO:root:pieca_20260604.csv written!
$ cat pieca_20260604.json | jq .[0]
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
  "title_type": "movie",
  "title_sub_type": "film_cinema",
  "url": "https://www.filmweb.pl/film/Wej%C5%9Bcie+smoka%21-2016-757318",
  "date": "2020-01-18"
}
$ duckdb -box -c "SELECT * FROM read_csv_auto('pieca_20260604.csv') ORDER BY RANDOM() LIMIT 3;"
┌───────────────┬──────────┬─────────────┬───────────────┬─────────────────────┬─────────────────┬─────────────────┬──────┬──────────┬────────────┬────────────────┬────────────────────────────────────────────────────────────────────┬────────────┐
│   timestamp   │ favorite │ user_rating │ global_rating │ global_rating_count │ original_title  │    pl_title     │ year │ movie_id │ title_type │ title_sub_type │                                url                                 │    date    │
├───────────────┼──────────┼─────────────┼───────────────┼─────────────────────┼─────────────────┼─────────────────┼──────┼──────────┼────────────┼────────────────┼────────────────────────────────────────────────────────────────────┼────────────┤
│ 1552236606975 │ NULL     │ 7           │ 6.60002       │ 25576               │ Force Majeure   │ Turysta         │ 2014 │ 709434   │ movie      │ film_cinema    │ https://www.filmweb.pl/film/Turysta-2014-709434                    │ 2019-03-10 │
│ 1638616857444 │ NULL     │ 5           │ 7.27418       │ 60056               │ Pogoda na jutro │ Pogoda na jutro │ 2003 │ 39495    │ movie      │ film_cinema    │ https://www.filmweb.pl/film/Pogoda+na+jutro-2003-39495             │ 2021-12-04 │
│ 1638614791800 │ NULL     │ 6           │ 7.69933       │ 51552               │ Żółty szalik    │ Żółty szalik    │ 2000 │ 32453    │ movie      │ film_tv        │ https://www.filmweb.pl/film/%C5%BB%C3%B3%C5%82ty+szalik-2000-32453 │ 2021-12-04 │
└───────────────┴──────────┴─────────────┴───────────────┴─────────────────────┴─────────────────┴─────────────────┴──────┴──────────┴────────────┴────────────────┴────────────────────────────────────────────────────────────────────┴────────────┘

```

#### Dowolne filmy

```bash
$ filmweb --stdout details 529 80 | jq
INFO:filmweb.main:Fetching info about titles [1/2]...
100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 2/2 [00:00<00:00,  6.76it/s]
INFO:filmweb.main:Fetching global rating for titles [2/2]...
100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 2/2 [00:00<00:00,  6.86it/s]
INFO:filmweb.parser:Writing data...
[
  {
    "movie_id": 529,
    "duration": 104,
    "poster_url": "https://fwcdn.pl/fpo/05/29/529/8160166.10.webp",
    "pl_title": "Kiler",
    "original_title": "Kiler",
    "year": 1997,
    "title_type": "movie",
    "title_sub_type": "film_cinema",
    "plot": "Jerzy Kiler, warszawski taksówkarz, przypadkowo zostaje wzięty za płatnego zabójcę i umieszczony w areszcie. Wyciąga go stamtąd boss świata przestępczego, który oferuje mu nowe zadanie.",
    "genres": [
      "Komedia",
      "Sensacyjny"
    ],
    "directors": [
      "Juliusz Machulski"
    ],
    "countries": [
      "PL"
    ],
    "global_rating": 7.73682,
    "global_rating_count": 471324,
    "global_rating_histogram": {
      "1": 1832,
      "2": 1426,
      "3": 3551,
      "4": 6894,
      "5": 15654,
      "6": 40939,
      "7": 109851,
      "8": 160761,
      "9": 79472,
      "10": 50944
    }
  },
  {
    "movie_id": 80,
    "duration": 113,
    "poster_url": "https://fwcdn.pl/fpo/00/80/80/8023222_1.10.webp",
    "pl_title": "Kiler-ów 2-óch",
    "original_title": "Kiler-ów 2-óch",
    "year": 1999,
    "title_type": "movie",
    "title_sub_type": "film_cinema",
    "plot": "Jurek Kiler stał się sławną osobą, lecz gangsterzy, których oszukał, planują zemstę.\n",
    "genres": [
      "Komedia",
      "Sensacyjny"
    ],
    "directors": [
      "Juliusz Machulski"
    ],
    "countries": [
      "PL"
    ],
    "global_rating": 7.2879,
    "global_rating_count": 238399,
    "global_rating_histogram": {
      "1": 990,
      "2": 953,
      "3": 2935,
      "4": 5672,
      "5": 13875,
      "6": 34054,
      "7": 71860,
      "8": 64421,
      "9": 25437,
      "10": 18202
    }
  }
]
```

### Wszystkie opcje

```bash
$ filmweb -h
filmweb

Usage:
    filmweb details [--format=<fileformat>]... [--stdout] [--workers=<n>] [--debug] <id>...
    filmweb [--format=<fileformat>]... [--stdout] [--type=<titletype>]... [--workers=<n>] [--pages=<range>] [--since=<date>] [--debug] <username> <cookie>

Options:
    -h --help                     Show this screen
    -f --format=<fileformat>      Output file format: json (default), csv, letterboxd
    -o --stdout                   Print result to stdout instead of file
    -t --type=<titletype>         Title type: movie, tv_show, game (default: all)
    -w --workers=<n>              Number of parallel workers (default: CPU count)
    -p --pages=<range>            Fetch only given pages of ratings list (100 titles per page),
                                  e.g. 3 or 2-5 or 4- (default: all pages)
    -s --since=<date>             Export only titles rated (or re-rated) on or after
                                  given date, inclusive, format YYYY-MM-DD
                                  (default: all titles)
    -d --debug                    Debug prints

Source:
    https://github.com/ppatrzyk/filmweb-export
```

## Dostępne dane:

Kolumna | Opis
--- | ---
movie\_id | _id filmu_ (filmweb)
timestamp | _[czas oceny (unix)](https://pl.wikipedia.org/wiki/Czas_uniksowy)_
date | _data oceny_ (yyyy-mm-dd)
favorite | _dodany do ulubionych_
user\_rating | _ocena użytkownika_
global\_rating | _ocena filmweb_
global\_rating\_count | _ilość ocen filmu_
global\_rating\_histogram | _rozkład ocen filmu_
year | _premiera_
duration | _czas trwania w minutach_
original\_title | _tytuł oryginalny_
pl\_title | _tytuł polski_
title\_type | _typ tytułu_ (movie, tv\_show, game)
title\_sub\_type | _podtyp tytułu_ (np. serial\_tv, mini\_serial)
plot | _opis_
url | _strona filmu_
poster\_url | _adres plakatu_
genres | _gatunki_
countries | _kraje produkcji_
directors | _reżyserzy_

## DEV

Lokalna instalacja:

```bash
pip3 install -e .[dev]
```

Pyinstaller:

```bash
pyinstaller --distpath pyinstaller_dist --workpath pyinstaller_build packaging/filmweb.spec
```

Wynik znajdziesz w katalogu `pyinstaller_dist/`.

Docker:

```bash
podman build -t ghcr.io/ppatrzyk/filmweb-export:dev .
```
