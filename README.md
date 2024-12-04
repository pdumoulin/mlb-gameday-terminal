# :baseball: mlb-gameday-terminal :baseball:

![Final Game Output Screenshot](/screenshots/game_final.png?raw=true)

## Quickstart

1. Build image

```bash
$ docker compose build
```

2. Set an alias for easy usage anywhere (syntax used in rest of this guide)

```bash
$ alias mlb='docker compose -f ~/projects/mlb-gameday-terminal/docker-compose.yaml run --rm app'
```

3. Get live data and exit

```bash
$ mlb query --team nym
```

4. Watch live data, updated every minute, changes highlighted
```bash
$ export WATCH_MLB=60 && mlb query --team nym
```

5. Load data from past game

```bash
$ mlb query --team nym --date 2019-09-27
```

:information_source: You can search for a team by any term that partially matches exactly one team by either name, location, or abbreviation.

## Update Teams List

By default teams with the names, abbreviations, and IDs are stored in `teams.py`. In the unlikely event you need to update that list, run the following...

```bash
$ python fetch_team_ids.py > teams.py
```

## Use Sample Data

Repo includes past games in certain states in **games.p** for easier debugging and development.

### Save Sample Game

```bash
$ mlb save --team nym --date 2019-09-27 --name pete-alonso
```

### List Available Sample Games

```bash
$ mlb load
```

### Load Sample Game

```bash
$ mlb load --name pete-alonso
```

## Help

### Query

```bash
usage: run.py query [-h] --team TEAM [--date DATE] [--select {all,first,second,smart}]

optional arguments:
  -h, --help            show this help message and exit
  --team TEAM           team search term partical match for name, location, or abbreviation
  --date DATE           YYYY-MM-DD date to find game for, default today
  --select {all,first,second,smart}
                        filter games list
```

### Save

```bash
python run.py save --help
usage: run.py save [-h] --team TEAM [--date DATE] --name NAME

optional arguments:
  -h, --help   show this help message and exit
  --team TEAM  team search term partical match for name, location, or abbreviation
  --date DATE  YYYY-MM-DD date to find game for, default today
  --name NAME  Save raw game data with input name to test with later
```

### Load

```bash
python run.py load --help
usage: run.py load [-h] [--name NAME]

optional arguments:
  -h, --help   show this help message and exit
  --name NAME  Load raw game data with input name instead of querying
  --select {all,first,second,smart}
                        filter games list
```
