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

## Run Script
1. Activate virtual env (see install above)
2. Run script

Today:
```
$ python run.py --team nym
```
Past Game:
```
$ python run.py --team nym --date 2019-09-27
```
Details:
```
python run.py --help
usage: run.py [-h] --team TEAM [--date DATE]

optional arguments:
  -h, --help   show this help message and exit
  --team TEAM  team to find game for
  --date DATE  YYYY-MM-DD date to find game for
```
## Auto Update
```
$ watch -d -n 60 "python run.py --team nym"
```
