# :baseball: mlb-gameday-terminal :baseball:

![Final Game Output Screenshot](/screenshots/game_final.png?raw=true)

## Quickstart
1. Get live data
```
run.sh nym
```
2. Watch live data, updated every minute
```
run.sh nym 60
```
:information_source: You can search for a team by any term that partially matches exactly one team by either name, location, or abbreviation.
## Install Requirements
**If you ran quickstart script, this was done already.**
1. Create virtual env
```
$ python -m venv env
```
2. Activate virtual env
```
$ source env/bin/activate
```
3. Install packages
```
$ pip install -r requirements.txt
```

## Query for Game Data
1. Activate virtual env (see install above)
2. Run script

### Today
```
$ python run.py query --team nym
```
### Past Game
```
$ python run.py query --team nym --date 2019-09-27
```
### Auto Update
```
$ watch -t -d -n 60 "python run.py query --team nym"
```
## Update Teams List
By default teams with the names, abbreviations, and IDs are stored in `teams.py`. In the unlikely event you need to update that list, run the following...
```
$ python fetch_team_ids.py > teams.py
```

## Use Sample Data
Repo includes past games in certain states in **games.p** for easier debugging and development.

### Save Sample Game
```
$ python run.py save --team nym --date 2019-09-27 --name pete-alonso
```
### List Available Sample Games
```
$ python run.py load
```
### Load Sample Game
```
$ python run.py load --name pete-alonso
```
## Help

### Query
```
usage: run.py query [-h] --team TEAM [--date DATE] [--select {all,first,second}]

optional arguments:
  -h, --help            show this help message and exit
  --team TEAM           team search term partical match for name, location, or abbreviation
  --date DATE           YYYY-MM-DD date to find game for, default today
  --select {all,first,second}
                        filter games list
```

### Save
```
python run.py save --help
usage: run.py save [-h] --team TEAM [--date DATE] --name NAME

optional arguments:
  -h, --help   show this help message and exit
  --team TEAM  team search term partical match for name, location, or abbreviation
  --date DATE  YYYY-MM-DD date to find game for, default today
  --name NAME  Save raw game data with input name to test with later
```

### Load
```
python run.py load --help
usage: run.py load [-h] [--name NAME]

optional arguments:
  -h, --help   show this help message and exit
  --name NAME  Load raw game data with input name instead of querying
  --select {all,first,second}
                        filter games list
```
