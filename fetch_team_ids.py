"""Export team configuration."""
# https://appac.github.io/mlb-data-api-docs/#team-data-list-teams-get

import datetime
import sys

import requests

year = sys.argv[1] if len(sys.argv) > 1 else datetime.datetime.now().year
url = 'https://lookup-service-prod.mlb.com/json/named.team_all_season.bam'
params = {
    'sport_code': "'mlb'",
    'season': year
}
response = requests.get(url, params=params)
data = response.json()
teams = [
    {
        'id': x['team_id'],
        'name': x['name_display_full'],
        'abbr': x['mlb_org_abbrev']
    }
    for x in data['team_all_season']['queryResults']['row']
    if x['mlb_org'] != ''
]
print(f'TEAMS = {teams}')
