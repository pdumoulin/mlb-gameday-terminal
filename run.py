
import random

import mlbgame

from tabulate import tabulate

def main():

    # TODO - add CLI args (team, auto refresh until final)

    team = 'mets'.title()

    games = mlbgame.day(2019, 9, 27, home=team, away=team)
    game = games[0]

    # print(game.__dict__)

    box_score = mlbgame.box_score(game.game_id)
    list_score = list_score_table(game, box_score)
    print(list_score)
    print(game.game_status)

    # TODO - maybe use JSON web api, parts of this package are broken

    # TODO - add player stats, event stream

    # TODO - add broadcast info

    # broken
    # player_stats = mlbgame.player_stats(game.game_id)
    # print(player_stats)

    # broken
    # team_stats = mlbgame.team_stats(game.game_id)
    # print(team_stats)


def list_score_table(game, box_score):
    home_team = game.home_team
    home_team_hits = game.home_team_hits
    home_team_runs = game.home_team_runs
    home_team_errors = game.home_team_errors

    away_team = game.away_team
    away_team_hits = game.away_team_hits
    away_team_runs = game.away_team_runs
    away_team_errors = game.away_team_errors

    inning_scores = box_score.innings
    placeholders = ['-'] * (9 - len(inning_scores))
    home_inning_scores = [x['home'] for x in inning_scores] + placeholders
    away_inning_scores = [x['away'] for x in inning_scores] + placeholders

    table_format = 'fancy_grid'

    labels = tabulate(
        [
            [away_team],
            [home_team]
        ],
        headers=[''],
        tablefmt=table_format,
        stralign='left'
    )
    innings = tabulate(
        [
            away_inning_scores,
            home_inning_scores
        ],
        headers=range(1, len(home_inning_scores) + 1),
        tablefmt=table_format,
        numalign='center',
        stralign='center'
    )
    totals = tabulate(
        [
            [away_team_runs, away_team_hits, away_team_errors],
            [home_team_runs, home_team_hits, home_team_errors],
        ],
        headers=['R', 'H', 'E'],
        tablefmt=table_format,
        numalign='right'
    )

    merged = merge_tables(labels, innings)
    return merge_tables(merged, totals)


def merge_tables(left, right):
    left_split = left.split('\n')
    right_split = right.split('\n')
    left_width = max([len(x) for x in left_split])
    larger_size = max(len(left_split), len(right_split))
    result = [None] * larger_size
    for i in range(0, larger_size):
        if i < len(left_split):
            result[i] = left_split[i]
        else:
            result[i] = ' ' * left_width
        if i < len(right_split):
            result[i] += right_split[i]
    return '\n'.join(result)


if __name__ == '__main__':
    main()
