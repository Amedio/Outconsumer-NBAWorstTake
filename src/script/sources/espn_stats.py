from datetime import date, datetime, timedelta
import json
import sys
from time import sleep
from urllib.request import urlopen, Request

from pprint import pprint
import source


class espn_stats:
    """Gathers interesting statistics about games and team standings"""

    standings = None

    def __init__(self, return_format='id'):
        self.custom_headers = {
            'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/111.0.0.0 Safari/537.36'),
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.espn.com/nba/',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache'
        }
        self.return_format = return_format

    def get_events(self, a_date):
        """Return the last games finished within the last 3 days"""
        d = a_date.strftime("%Y%m%d")
        url = f"http://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates={d}"
        print(f"Reading {url}...")
        request = Request(url, headers=self.custom_headers)
        json_url = urlopen(request)
        data = json.loads(json_url.read())
        sleep(1)
        return data

    def get_games_dated(self, a_date):
        """Return the last games finished within the last 3 days"""
        data = self.get_events(a_date)
        sleep(1)
        games = []
        for event in data['events']:
            if event['status']['type']['completed']:  # skip scheduled or live games
                if self.return_format == 'id':
                    games.append(event['id'])
                else:
                    games.append(event)
        return games

    def get_last_finished_games(self, days=3):
        """Return the last games finished within the last 3 days"""
        games = []
        for day_offset in range(0, days):
            d = date.today() - timedelta(days=day_offset)
            games.extend(self.get_games_dated(d))
        return games

    def get_sources(self):
        """Returns a list of sources from the last finished games"""
        sources = []
        for game_id in self.get_last_finished_games():
            sources.append(source.source(game_id, 'espn_stats', datetime.now()))
        return sources

    def get_game_details(self, game_id):
        """provides details of the given game id"""
        url = f"http://site.api.espn.com/apis/site/v2/sports/basketball/nba/summary?event={game_id}"
        print(f"Reading {url}...")
        request = Request(url, headers=self.custom_headers)
        json_url = urlopen(request)
        data = json.loads(json_url.read())
        sleep(1)
        return data

    def get_game_list_details(self, game_list):
        # retrieve game stats
        games = []
        for game in game_list:
            game_details = self.get_game_details(game)
            games.append(game_details)
        return games

    def normalize_number(self, number):
        """convert sometimes float numbers into integers"""
        if number is None or type(number) == int:
            return number
        return int(float(number))

    def normalize_time(self, time):
        """convert sometimes float minutes into mm:ss format"""
        if time is None or ':' not in time:
            return time
        time_split = time.split(':')
        return (str(self.normalize_number(time_split[0])) + ':' +
                ':'.join([str(self.normalize_number(x)).zfill(2) for x in time_split[1:]]))

    def pluralize(self, stat, singular_name):
        stat = int(stat)
        if stat == 0:
            return ""
        if stat == 1:
            return f" 1 {singular_name}."
        else:
            return f" {stat} {singular_name}s."

    def create_player_summary(self, player, keys):
        """
        Generates a text summary for the given player
        """
        player_name = player['athlete']['displayName']
        if player['didNotPlay']:
            return f"\t{player_name} didn't play ({player['reason']})."

        stats = dict(zip(keys, player['stats']))
        text = (f"\t{player_name} played {stats['minutes']} minutes, "
                f"scored {stats['points']} points, caught {stats['rebounds']} rebounds "
                f"and made {stats['assists']} assists.")
        # only add these stats if not zero
        text += self.pluralize(stats['steals'], "steal")
        text += self.pluralize(stats['turnovers'], "turnover")
        threes = stats["threePointFieldGoalsMade-threePointFieldGoalsAttempted"].split("-")[0]
        text += self.pluralize(threes, "three")

        return text

    def create_players_summary(self, team_stats):
        """
        Generate a text-based summary of all players performances in a game
        from the given team
        """
        summary = ""
        for player in team_stats['athletes']:
            summary += self.create_player_summary(player, team_stats['keys'])
            summary += '\n'
        return summary
        
    def create_team_summary(self, team_name, team_stats):
        """
        return the points and a text description of the given team_id from the list
        of team results.
        """
        # get properties
        totals = dict(zip(team_stats['keys'], team_stats['totals']))
        return (int(totals['points']),
                (f"{team_name} scored {totals['points']} points, got {totals['rebounds']} rebounds, "
                 f"did {totals['assists']} assists and {totals['steals']} steals. "
                 f"Game turnovers: {totals['turnovers']}."))

    def create_game_summary(self, game):
        """Generate a human-readable text summary for a given game"""
        away_team = game['boxscore']['teams'][0]['team']['displayName']
        away_team_stats = game['boxscore']['players'][0]['statistics'][0]
        home_team = game['boxscore']['teams'][1]['team']['displayName']
        home_team_stats = game['boxscore']['players'][1]['statistics'][0]
        venue = game['gameInfo']['venue']['fullName']
        away_team_pts, away_team_summary = self.create_team_summary(away_team, away_team_stats)
        away_team_players_summary = self.create_players_summary(away_team_stats)
        home_team_pts, home_team_summary = self.create_team_summary(home_team, home_team_stats)
        home_team_players_summary = self.create_players_summary(home_team_stats)
        winning_team = away_team if away_team_pts > home_team_pts else home_team

        text = f"""
The final score was:

{away_team} {away_team_pts} - {home_team_pts} {home_team}

The game was played at {venue}.

{away_team_summary}
{home_team_summary}

{away_team} played with the following players:
{away_team_players_summary}

{home_team} played with the following players:
{home_team_players_summary}

{winning_team} won!
"""
        return text

    def generate_prompt(self, s):
        """
        Given a source s containing as identifier a game_id, query the game details
        and return a text summary of it to be used as a prompt
        """
        game_details = self.get_game_details(s.id)
        return self.create_game_summary(game_details)

    def print_game_data(self, game):
        home_pts, _ = self.create_team_summary(game['stats']['TeamStats'], game['home_team']['id'])
        home_team = game['home_team']['full_name']
        visitor_team = game['visitor_team']['full_name']
        visitor_pts, _ = self.create_team_summary(game['stats']['TeamStats'], game['visitor_team']['id'])

        return (f"{visitor_team} **{visitor_pts}** - "
                f"**{home_pts}** {home_team}\n")

    def get_standings(self, conference):
        """return the list of standings of both conferences"""
        #TODO
        self.standings = {'east': [],
                          'west': []}

    def print_standings(self, conference):
        yield(f"*__{conference.upper()}__*\n")
        for team in self.standings.get(conference):
            team_name = teams.find_team_name_by_id(team['TEAM_ID'])['nickname']
            yield((f"**{team_name}** games: {team['G']}, wins: {team['W']}, "
                   f"losses: {team['L']}, win percentage: {team['W_PCT']}\n"))
        return

    def list_games(self):
        games = self.get_last_finished_games()
        game_text = ""
        for game in games:
            sleep(1)
            pprint(self.get_game_details(game))
            sys.exit(0)
            game_text += self.print_game_data(self.get_game_details(game))
        return game_text

    def list_standings(self, conference):
        if self.standings is None:
            self.get_standings(conference)
        standings = ""
        for s in self.print_standings(conference):
            standings += s
        return standings


def main():
    if sys.argv[1] == 'standings':
        nba = nba_stats()
        print(nba.list_standings('east'))
        print(nba.list_standings('west'))
    elif sys.argv[1] == 'games':
        nba = nba_stats()
        print(nba.list_games())


if __name__ == "__main__":
    main()
