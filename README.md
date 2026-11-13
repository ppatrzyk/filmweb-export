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
    ghcr.io/ppatrzyk/filmweb-export:v0.15 \
    filmweb <username> <cookie>
```

### Gotowe binarki

Samodzielny plik wykonywalny zbudowany przy użyciu [PyInstaller](https://pyinstaller.org) (Linux, MacOS, Windows).

Pobierz z zakładki [Releases](https://github.com/ppatrzyk/filmweb-export/releases).

## Instrukcja

Zobacz też [przykłady](#przykład) wraz z danymi.

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

### Wyszukiwanie

```bash
filmweb search <query>
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
$ filmweb -f csv -f json -s 2021-01-01 pieca "didomi_token=(...)=="
INFO:filmweb.main:Fetching list of rated titles [1/3]...
INFO:filmweb.main:Skipping videogame, no ratings found
INFO:filmweb.main:Fetching list of serial ratings (pages 1-1 of 1)...
100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00,  2.82it/s]
INFO:filmweb.main:Fetching list of film ratings (pages 1-10 of 10)...
100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 10/10 [00:00<00:00, 15.31it/s]
INFO:filmweb.main:User pieca has 225 rated titles since 2021-01-01...
INFO:filmweb.main:Fetching info about titles [2/3]...
100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 225/225 [00:12<00:00, 17.53it/s]
INFO:filmweb.main:Fetching global rating for titles [3/3]...
100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 225/225 [00:10<00:00, 20.82it/s]
INFO:filmweb.writer:Writing data...
INFO:filmweb.writer:pieca_20261112.json written!
INFO:filmweb.writer:pieca_20261112.csv written!
$ cat pieca_20261112.json | jq .[0]
{
  "timestamp": 1743336683045,
  "movie_id": 10074202,
  "user_rating": 6,
  "duration": 57,
  "poster_url": "https://fwcdn.pl/fpo/42/02/10074202/8168022.10.webp",
  "pl_title": "Dojrzewanie",
  "original_title": "Adolescence",
  "year": 2025,
  "title_type": "tv_show",
  "title_sub_type": "serial_tv",
  "plot": "Trzynastolatek zostaje oskarżony o morderstwo koleżanki z klasy. Jego rodzina, terapeutka i prowadzący sprawę detektyw zadają sobie pytanie o to, co naprawdę się stało.",
  "genres": [
    "Dramat",
    "Psychologiczny",
    "Kryminał"
  ],
  "directors": [
    "Philip Barantini"
  ],
  "countries": [
    "GB"
  ],
  "url": "https://www.filmweb.pl/film/Dojrzewanie-2025-10074202",
  "global_rating": 7.69396,
  "global_rating_count": 97248,
  "global_rating_histogram": {
    "1": 460,
    "2": 263,
    "3": 818,
    "4": 1168,
    "5": 3649,
    "6": 8364,
    "7": 21015,
    "8": 35316,
    "9": 19902,
    "10": 6293
  }
}
$ duckdb -box -c "SELECT * FROM read_csv_auto('pieca_20261112.csv') ORDER BY RANDOM() LIMIT 1;"
┌──────────┬──────────┬────────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────┬───────────────────┬───────────────────┬──────┬────────────┬────────────────┬────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┬───────────────────────┬──────────────────────┬──────────────┬───────────────┬─────────────────────┬─────────────────────────────────────────────────────────────────────────────────────────────────────────┬───────────────┬──────────┬─────────────┐
│ movie_id │ duration │                              url                               │                     poster_url                      │     pl_title      │  original_title   │ year │ title_type │ title_sub_type │                                                                  plot                                                                  │        genres         │      directors       │  countries   │ global_rating │ global_rating_count │                                         global_rating_histogram                                         │   timestamp   │ favorite │ user_rating │
├──────────┼──────────┼────────────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────┼───────────────────┼───────────────────┼──────┼────────────┼────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼───────────────────────┼──────────────────────┼──────────────┼───────────────┼─────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────┼───────────────┼──────────┼─────────────┤
│ 857607   │ 98       │ https://www.filmweb.pl/film/Jak+najdalej+st%C4%85d-2020-857607 │ https://fwcdn.pl/fpo/76/07/857607/7930660_2.10.webp │ Jak najdalej stąd │ Jak najdalej stąd │ 2020 │ movie      │ film_cinema    │ Zbuntowana nastolatka, której ojciec zginął w wypadku na budowie, musi sama pojechać do Irlandii, aby sprowadzić ciało taty do Polski. │ ["Dramat", "Komedia"] │ ["Piotr Domalewski"] │ ["IE", "PL"] │ 6.81045       │ 20564               │ {"1": 36, "2": 34, "3": 131, "4": 324, "5": 1427, "6": 4895, "7": 9006, "8": 3921, "9": 558, "10": 232} │ 1638219848669 │ NULL     │ 8           │
└──────────┴──────────┴────────────────────────────────────────────────────────────────┴─────────────────────────────────────────────────────┴───────────────────┴───────────────────┴──────┴────────────┴────────────────┴────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┴───────────────────────┴──────────────────────┴──────────────┴───────────────┴─────────────────────┴─────────────────────────────────────────────────────────────────────────────────────────────────────────┴───────────────┴──────────┴─────────────┘

```

#### Dowolne filmy

```bash
$ filmweb --stdout details 529 80 | jq
INFO:filmweb.main:Fetching info about titles [1/2]...
100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 2/2 [00:00<00:00,  6.07it/s]
INFO:filmweb.main:Fetching global rating for titles [2/2]...
100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 2/2 [00:00<00:00,  6.52it/s]
INFO:filmweb.writer:Writing data...
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
    "actors": [
      "Cezary Pazura",
      "Małgorzata Kożuchowska"
    ],
    "url": "https://www.filmweb.pl/film/Kiler-1997-529",
    "global_rating": 7.73684,
    "global_rating_count": 471332,
    "global_rating_histogram": {
      "1": 1832,
      "2": 1425,
      "3": 3552,
      "4": 6894,
      "5": 15654,
      "6": 40940,
      "7": 109851,
      "8": 160764,
      "9": 79473,
      "10": 50947
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
      "Sensacyjny",
      "Komedia"
    ],
    "directors": [
      "Juliusz Machulski"
    ],
    "countries": [
      "PL"
    ],
    "actors": [
      "Cezary Pazura",
      "Janusz Rewiński"
    ],
    "url": "https://www.filmweb.pl/film/Kiler-%C3%B3w+2-%C3%B3ch-1999-80",
    "global_rating": 7.28797,
    "global_rating_count": 238401,
    "global_rating_histogram": {
      "1": 989,
      "2": 953,
      "3": 2936,
      "4": 5671,
      "5": 13875,
      "6": 34051,
      "7": 71862,
      "8": 64422,
      "9": 25438,
      "10": 18204
    }
  }
]
```

#### Wyszukiwanie

```bash
$ filmweb search --stdout --type film wściekłe pięści węża | jq
INFO:filmweb.main:Searching for 'wściekłe pięści węża'...
INFO:filmweb.main:Fetching search results for film (pages 1-1 of 1)...
100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00,  3.68it/s]
INFO:filmweb.writer:Writing data...
[
  {
    "movie_id": 389424,
    "type": "movie",
    "matched_title": "Wściekłe pięści węża 2",
    "matched_lang": "pl-PL",
    "actors": [
      "Łukasz Walaszek",
      "Dr Yry"
    ]
  },
  {
    "movie_id": 311861,
    "type": "movie",
    "matched_title": "Wściekłe pięści Węża",
    "matched_lang": "pl-PL",
    "actors": [
      "Monika Szczęk",
      "Mirosław Jędras"
    ]
  },
  {
    "movie_id": 704550,
    "type": "movie",
    "matched_title": "Wściekłe pięści Węża 3",
    "matched_lang": "pl-PL",
    "actors": [
      "Bartosz Walaszek",
      "Grzegorz Zacharjasiewicz"
    ]
  }
]
```

### Wszystkie opcje

```bash
$ filmweb -h
filmweb

Usage:
    filmweb details [--format=<fileformat>]... [--stdout] [--workers=<n>] [--debug] <id>...
    filmweb search [--format=<fileformat>]... [--stdout] [--type=<titletype>]... [--pages=<range>] [--workers=<n>] [--debug] <query>...
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
movie\_id | _id filmu_
timestamp | _[czas oceny (unix)](https://pl.wikipedia.org/wiki/Czas_uniksowy)_ (user export)
date | _data oceny_ (user export)
favorite | _dodany do ulubionych_ (user export)
user\_rating | _ocena użytkownika_ (user export)
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
actors | _aktorzy_

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
