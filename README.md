# mlb-gameday-terminal

## Install Requirements
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
4. Download team ID mappings
```
$ python fetch_team_ids.py > teams.py
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
$ watch -d -n 60 "python run.py query --team nym"
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
python run.py query --help
usage: run.py query [-h] --team TEAM [--date DATE]

optional arguments:
  -h, --help   show this help message and exit
  --team TEAM  team to find game for
  --date DATE  YYYY-MM-DD date to find game for, default today
```

### Save
```
python run.py save --help
usage: run.py save [-h] --team TEAM [--date DATE] --name NAME

optional arguments:
  -h, --help   show this help message and exit
  --team TEAM  team to find game for
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
```
