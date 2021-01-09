"""Terminal GameDay."""

import argparse
import datetime
import pickle

import requests

from rich import box
from rich.align import Align
from rich.console import Console
from rich.table import Table

from teams import TEAMS

# markers for base runners and count
# https://github.com/willmcgugan/rich/blob/master/rich/_emoji_codes.py
ON = ':black_medium_square:'
OFF = ':white_medium_square:'

# file to save/load game data for offline access
PICKLE_FILE = 'games.p'

# groups of game status to determine output format
GAME_STATUSES = {
    'pending': ['scheduled', 'pre-game', 'warmup', 'postponed', 'delayed start'],  # noqa:E501
    'live': ['in progress', 'delayed', 'challenge'],
    'finished': ['final', 'game over', 'completed', 'completed early']
}

# options to filter games list
SELECT_ALL = 'all'
SELECT_FIRST = 'first'
SELECT_SECOND = 'second'
SELECT_SMART = 'smart'

QUERY_CMD = 'query'
LOAD_CMD = 'load'
SAVE_CMD = 'save'


def main():
    """Overall flow control."""
    args = _load_args()
    command = args.command

    # parse commands and load games
    if command == LOAD_CMD:
        games = _load_game_data(args.name)
    else:
        team = _find_team(args.team)
        games = _find_games(args.date, team['id'])
        if not games:
            exit(f'Unable to find game on {args.date} for team {args.team}')
        if command == 'save':
            _save_game_data(args.name, games)

    # handle double headers
    filtered_games = _select_games(args.select, games)

    # generate rows of data from each game
    final_rows = []
    for game in filtered_games:
        final_rows += _game_rows(game)

    # add all rows in grid, centered
    grid = Table.grid()
    for x in final_rows:
        grid.add_row(Align.center(x))

    # print to console
    console = Console()
    console.print(grid, justify='center')

    # warn if double-header but only showing one
    if len(filtered_games) != len(games):
        final_rows.append(['* Not all games visible: change select arg to see all *'])  # noqa: E501


def _select_games(select, games):
    # take only first 2 games, sometimes there is excess data
    games = games[:2]
    if len(games) == 1:
        return games
    if select == SELECT_FIRST:
        return [games[0]]
    elif select == SELECT_SECOND:
        if len(games) < 2:
            exit('No second game found.')
        return [games[1]]
    elif select == SELECT_SMART:
        for game in games:
            if _game_live(game['_status']):
                return [game]
        for game in games:
            if _game_pending(game['_status']):
                return [game]
    return games


def _game_rows(game_details):
    summary = summary_table(game_details)
    box_score = box_score_table(game_details)
    broadcast = broadcast_table(game_details)
    probable_pitchers = probable_pitchers_table(game_details)
    (labels, innings, totals) = line_score_tables(game_details)
    bases = bases_table(game_details)
    count = count_table(game_details)

    result = []
    if _game_finished(game_details['_status']):
        top = Table.grid(expand=True)
        top.add_column(ratio=25)
        top.add_column(ratio=50)
        top.add_column(ratio=25)
        top.add_row(None, summary, None)
        top.add_row(
            Align.right(labels),
            Align.center(innings),
            Align.left(totals)
        )
        result.append(top)
        result.append(box_score)
    elif _game_live(game_details['_status']):
        top = Table.grid(expand=True)
        top.add_column(ratio=25)
        top.add_column(ratio=50)
        top.add_column(ratio=25)
        top.add_row(
            Align.right(bases),
            Align.center(summary),
            Align.left(count)
        )
        top.add_row(
            Align.right(labels),
            Align.center(innings),
            Align.left(totals)
        )
        result.append(top)
        result.append(box_score)
        result.append(broadcast)
    elif _game_pending(game_details['_status']):
        summary.expand = False
        result.append(summary)
        result.append(probable_pitchers)
        result.append(box_score)
        result.append(broadcast)
    else:
        print(f"{game_details['_status']} is unexpected game status")
        exit()

    return result


def summary_table(game_details, table_format='simple'):
    """Text overview of game."""
    game_data = game_details['gameData']

    game_status = game_data['status']['detailedState']
    game_time = game_data['datetime']
    venue = game_data['venue']
    weather = game_data['weather']

    away_team = game_data['teams']['away']
    home_team = game_data['teams']['home']

    if _game_live(game_details['_status']):
        line_score = game_details['liveData']['linescore']
        current_inning = line_score['currentInning']
        half = line_score['inningHalf']
        game_status += f' - {half} {current_inning}'

    def format_team(team):
        return f"{team['name']} ({team['record']['wins']} - {team['record']['losses']})"  # noqa:E501

    format_time = f"{game_time['time']} {game_time['ampm']}"  # local time
    format_venue = f"{venue['name']} : {venue['location']['city']}, {venue['location']['stateAbbrev']}"   # noqa:E501
    format_weather = f"{weather['temp']}°F {weather['condition']} : Wind {weather['wind']}" if 'temp' in weather else '-'  # noqa:E501

    table = Table(box=box.HORIZONTALS, show_header=False, expand=True)
    table.add_column(justify='center')
    table.add_row(f'{format_team(away_team)} @ {format_team(home_team)}')
    table.add_row(f'{format_time} {format_venue}')
    table.add_row(format_weather)
    table.add_row(game_status)
    return table


def broadcast_table(game_details, table_format='simple'):
    """Text details of TV and Radio broadcasts."""
    broadcasts = game_details['broadcasts']

    def format_broadcast(medium):
        filtered = ', '.join(
            sorted(set(
                [
                    x['name']
                    for x in broadcasts
                    if x['type'].lower() == medium.lower()
                ]
            ))
        )
        return f'{medium.upper()}: {filtered}' if filtered else None

    broadcast_mediums = ['tv', 'fm', 'am']
    table = Table(box=box.HORIZONTALS, show_header=False)
    table.add_column(justify='center')
    for medium in broadcast_mediums:
        line = format_broadcast(medium)
        if line:
            table.add_row(line)
    return table


def probable_pitchers_table(game_details, table_format='fancy_grid'):
    """Table of probably pitchers and their stats overview."""
    game_data = game_details['gameData']
    live_data = game_details['liveData']
    box_score = live_data['boxscore']
    pitchers = game_data.get('probablePitchers')

    def format_pitcher(team):
        team_name = box_score['teams'][team]['team']['name']
        pitcher = pitchers.get(team)
        if pitcher:
            pid = pitchers[team]['id']
            pitcher = box_score['teams'][team]['players'][f'ID{pid}']
            stats = pitcher['seasonStats']['pitching']
            return [
                team_name,
                pitcher['person']['fullName'],
                str(stats['gamesPlayed']),
                str(stats['inningsPitched']),
                str(stats['wins']),
                str(stats['losses']),
                str(stats['saves']),
                str(stats['era']),
                str(stats['strikeOuts']),
                str(stats['baseOnBalls'])
            ]
        else:
            return [team_name] + [''] * 9

    table = Table(expand=True, show_lines=True)
    for x in ['', 'Probable Pitchers', 'GP', 'IP', 'W', 'L', 'S', 'ERA', 'SO', 'BB']:  # noqa:E501
        table.add_column(x)
    table.add_row(*format_pitcher('away'))
    table.add_row(*format_pitcher('home'))
    return table


def box_score_table(game_details, allow_empty=False):
    """Table box score of both teams, hitting and pitching."""
    live_data = game_details['liveData']
    box_score = live_data['boxscore']

    home_team = box_score['teams']['home']['team']['name']
    away_team = box_score['teams']['away']['team']['name']

    def lineup(team, box_score):
        players = box_score['teams'][team]['players']
        active_players = [x for _, x in players.items() if 'battingOrder' in x]
        return sorted(active_players, key=lambda k: k['battingOrder'])

    offense = live_data['linescore']['offense'].get('batter', {})
    batter_id = offense.get('id', None)
    away_lineup = lineup('away', box_score)
    home_lineup = lineup('home', box_score)
    if not allow_empty and not away_lineup and not home_lineup:
        return ''

    table = Table(show_lines=True)
    table.add_column(home_team, justify='center')
    table.add_column(away_team, justify='center')
    table.add_row(
        Align.center(box_score_batting_table(away_lineup, batter_id)),
        Align.center(box_score_batting_table(home_lineup, batter_id))
    )
    table.add_row(
        Align.center(box_score_pitching_table('away', live_data)),
        Align.center(box_score_pitching_table('home', live_data))
    )
    return table


def box_score_batting_table(lineup, current_batter, table_format='simple'):
    """Table of batting box score for one team."""
    def display_order(batter):
        batting_order = int(batter['battingOrder'])
        if not batting_order % 100:
            return str(int(batting_order / 100))
        return ''

    def player_name(batter, current_batter):
        modifier = '*' if batter['id'] == current_batter else ' '
        return f"{modifier} {batter['fullName']}"

    table = Table(box=box.SIMPLE)
    for x in ['#', 'POS', 'Name', 'AB', 'H', 'R', 'RBI', 'BB', 'SO']:
        table.add_column(x)
    for x in lineup:
        table.add_row(
            display_order(x),
            x['position']['abbreviation'],
            player_name(x['person'], current_batter),
            str(x['stats']['batting']['atBats']),
            str(x['stats']['batting']['hits']),
            str(x['stats']['batting']['runs']),
            str(x['stats']['batting']['rbi']),
            str(x['stats']['batting']['baseOnBalls']),
            str(x['stats']['batting']['strikeOuts'])
        )
    return table


def box_score_pitching_table(team, live_data, table_format='simple'):
    """Table of pitching box score for one team."""
    # parse live events to find pitchers in game order
    plays = live_data['plays']['allPlays']
    pitcher_ids = {
        x['matchup']['pitcher']['id']: 1
        for x in plays
        if (
            x['about']['isTopInning'] and team == 'home'
            or
            not x['about']['isTopInning'] and team == 'away'
        )
    }.keys()
    pitchers = [
        live_data['boxscore']['teams'][team]['players'][f'ID{x}']
        for x in pitcher_ids
    ]

    table = Table(box=box.SIMPLE)
    for x in ['Name', 'IP', 'H', 'R', 'ER', 'BB', 'SO']:
        table.add_column(x)
    for x in pitchers:
        table.add_row(
            x['person']['fullName'],
            str(x['stats']['pitching']['inningsPitched']),
            str(x['stats']['pitching']['hits']),
            str(x['stats']['pitching']['runs']),
            str(x['stats']['pitching']['earnedRuns']),
            str(x['stats']['pitching']['baseOnBalls']),
            str(x['stats']['pitching']['strikeOuts'])
        )
    return table


def line_score_tables(game_details, table_format='fancy_grid'):
    """Table for top per-inning score."""
    live_data = game_details['liveData']
    box_score = live_data['boxscore']
    line_score = live_data['linescore']

    home_team = box_score['teams']['home']['team']['name']
    home_team_hits = line_score['teams']['home'].get('hits', 0)
    home_team_runs = line_score['teams']['home'].get('runs', 0)
    home_team_errors = line_score['teams']['home'].get('errors', 0)

    away_team = box_score['teams']['away']['team']['name']
    away_team_hits = line_score['teams']['away'].get('hits', 0)
    away_team_runs = line_score['teams']['away'].get('runs', 0)
    away_team_errors = line_score['teams']['away'].get('errors', 0)

    inning_scores = line_score['innings']

    # fill in innings that have data so far (work for final games as well)
    home_inning_scores = []
    away_inning_scores = []
    placeholder = 'x' if _game_finished(game_details['_status']) else '-'
    if not _game_pending(game_details['_status']):
        current_inning = int(line_score['currentInning'])
        is_top = line_score['inningHalf'].lower() == 'top'
        inning_scores = inning_scores[0:current_inning]
        for inning in inning_scores:
            away_inning_scores.append(inning['away'].get('runs', 0))
            if inning['num'] == current_inning and is_top:
                home_inning_scores.append(placeholder)
            else:
                home_inning_scores.append(inning['home'].get('runs', 0))

    # cast as strings for rich.Table
    away_inning_scores = [str(x) for x in away_inning_scores]
    home_inning_scores = [str(x) for x in home_inning_scores]

    # fill in gaps if they exist
    scheduled_len = int(line_score['scheduledInnings'])
    placeholders = [placeholder] * (scheduled_len - len(inning_scores))
    home_inning_scores += placeholders
    away_inning_scores += placeholders

    if _game_finished(game_details['_status']):
        w_marker = 'W -'
        l_marker = 'L -'
        if away_team_runs > home_team_runs:
            away_team = f'{w_marker} {away_team}'
            home_team = f'{l_marker} {home_team}'
        elif home_team_runs > away_team_runs:
            away_team = f'{l_marker} {away_team}'
            home_team = f'{w_marker} {home_team}'

    labels = Table(show_lines=True, expand=False)
    labels.add_column(no_wrap=True)
    labels.add_row(away_team)
    labels.add_row(home_team)

    innings = Table(show_lines=True, expand=True)
    for x in range(1, len(home_inning_scores) + 1):
        innings.add_column(str(x), justify='center')
    innings.add_row(*away_inning_scores)
    innings.add_row(*home_inning_scores)

    totals = Table(show_lines=True)
    for x in ['R', 'H', 'E']:
        totals.add_column(x, justify='center')
    totals.add_row(
        str(away_team_runs),
        str(away_team_hits),
        str(away_team_errors)
    )
    totals.add_row(
        str(home_team_runs),
        str(home_team_hits),
        str(home_team_errors)
    )
    return (labels, innings, totals)


def bases_table(game_details):
    """Diamond for base runners."""
    live_data = game_details['liveData']
    offense = live_data['linescore']['offense']
    first = ON if 'first' in offense else OFF
    second = ON if 'second' in offense else OFF
    third = ON if 'third' in offense else OFF

    pad = 1
    bases = Table.grid(expand=True, padding=(pad, pad, pad, pad))

    bases = Table(
        box=box.HORIZONTALS,
        expand=False,
        show_header=False,
        show_footer=False,
        show_edge=False
    )
    bases.add_column(justify='center')
    bases.add_column(justify='center')
    bases.add_column(justify='center')
    bases.add_column(justify='center')
    bases.add_row()
    bases.add_row(' ', second, ' ')
    bases.add_row()
    bases.add_row(third, OFF, first)
    bases.add_row()
    return bases


def count_table(game_details):
    """Batting count."""
    live_data = game_details['liveData']

    def format_checks(label, num_checked, total):
        return [label] + [
            ON if x < num_checked else OFF
            for x in range(0, total)
        ]

    current_play = live_data['plays'].get('currentPlay', {})
    current_count = current_play.get('count', {})
    outs = current_count.get('outs', 0)
    strikes = current_count.get('strikes', 0) if outs != 3 else 0
    balls = current_count.get('balls', 0) if outs != 3 else 0

    table = Table(
        box=box.HORIZONTALS,
        expand=False,
        show_header=False,
        show_footer=False,
        show_edge=False
    )
    table.add_row()
    table.add_row(*format_checks('B', balls, 4))
    table.add_row(*format_checks('S', strikes, 3))
    table.add_row(*format_checks('O', outs, 3))
    table.add_row()
    return table


def _game_pending(status):
    return _check_status(status, 'pending')


def _game_live(status):
    return _check_status(status, 'live')


def _game_finished(status):
    return _check_status(status, 'finished')


def _check_status(status, target_status):
    status = status.split(':')[0]
    return status in GAME_STATUSES[target_status]


def _find_team(term):
    teams = [
        x for x in TEAMS
        if term in x['name'].lower() or term in x['abbr'].lower()
    ]
    if not teams:
        exit(f'Could not find team using search term "{term}"')
    elif len(teams) > 1:
        matches = [f"{x['name']} ({x['abbr']})" for x in teams]
        exit(f'Matched too many teams with search term "{term}" => {matches}')  # noqa:E501
    return teams[0]


def _find_games(day, team_id):
    url = 'https://statsapi.mlb.com/api/v1/schedule'
    params = {
        'date': day,
        'language': 'en',
        'sportId': 1,
        'teamId': team_id,
        'hydrate': 'broadcasts(all)'
    }
    response = requests.get(url, params=params)
    data = response.json()
    dates = data.get('dates', [])
    if not dates:
        return []
    return [_find_game_details(x) for x in dates[0]['games']]


def _find_game_details(game):
    game_id = game['gamePk']
    url = f'https://statsapi.mlb.com/api/v1.1/game/{game_id}/feed/live'
    response = requests.get(url)
    details = response.json()
    details['_status'] = details['gameData']['status']['detailedState'].lower()  # noqa:E501
    details['broadcasts'] = [
        x
        for x in game['broadcasts']
        if x['language'].lower() in ['en']
    ]
    return details


def _save_game_data(name, data):
    games = pickle.load(open(PICKLE_FILE, 'rb'))
    if name in games:
        exit(f'Game named "{name}" already exists in saved data!')
    games[name] = data
    pickle.dump(games, open(PICKLE_FILE, 'wb'))


def _load_game_data(name):
    games = pickle.load(open(PICKLE_FILE, 'rb'))
    if name not in games:
        print('\n'.join([x for x in games.keys()]))
        if name:
            exit(f'Unable to find game named "{name}" in saved data!')
        else:
            exit()
    return games[name]


def _delete_game_data(name):
    games = pickle.load(open(PICKLE_FILE, 'rb'))
    if name not in games:
        exit(f'Unable to find game named "{name}" in saved data!')
    del games[name]
    pickle.dump(games, open(PICKLE_FILE, 'wb'))


def _load_args():
    parser = argparse.ArgumentParser()

    # config for shorthand date options
    date_format = '%Y-%m-%d'
    quick_dates = {
        'today': datetime.date.today().strftime(date_format),
        'tomorrow': (datetime.datetime.today() - datetime.timedelta(days=-1)).strftime(date_format),  # noqa:E501
        'yesterday': (datetime.datetime.today() - datetime.timedelta(days=1)).strftime(date_format)  # noqa:E501
    }
    quick_date_opts = '{' + ','.join(quick_dates.keys()) + '}'

    subparsers = parser.add_subparsers(dest='command')
    parser_query = subparsers.add_parser(QUERY_CMD)
    parser_save = subparsers.add_parser(SAVE_CMD)
    parser_load = subparsers.add_parser(LOAD_CMD)
    for each in [parser_save, parser_query]:
        each.add_argument(
            '--team',
            required=True,
            help='team search term partical match for name, location, or abbreviation')  # noqa: E501
        each.add_argument(
            '--date',
            required=False,
            default='today',
            help=f'YYYY-MM-DD specific date or one of {quick_date_opts}')
    for each in [parser_query, parser_load]:
        each.add_argument(
            '--select',
            required=False,
            default=SELECT_ALL,
            choices=[
                SELECT_ALL,
                SELECT_FIRST,
                SELECT_SECOND,
                SELECT_SMART
            ],
            help='filter games list'
        )
    parser_save.add_argument(
        '--name',
        required=True,
        help='Save raw game data with input name to test with later')
    parser_load.add_argument(
        '--name',
        required=False,
        help='Load raw game data with input name instead of querying')
    args = parser.parse_args()

    # handle user not submitting command
    if not args.command:
        parser.print_help()
        exit()

    # convert date arg to formatted string
    if 'date' in args:
        if args.date in quick_dates.keys():
            args.date = quick_dates[args.date]
        else:
            try:
                datetime.datetime.strptime(args.date, date_format)
            except ValueError:
                exit(f'{args.date} not in format {date_format} or {quick_date_opts}')  # noqa:E501

    return args


if __name__ == '__main__':
    main()
