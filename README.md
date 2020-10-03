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

Filmweb wymaga zalogowania, aby uzyskać dostęp do wszystkich ocen. Istnieje możliwość eksportu własnych ocen:

```
todo
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
