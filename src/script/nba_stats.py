import sys
from time import sleep

#from pprint import pprint
from nba_api.stats.endpoints import Scoreboard, BoxScoreTraditionalV2
from nba_api.stats.static import teams


class nba_stats:
    """Gathers interesting statistics about games and team standings"""

    standings = None

    def __init__(self):
        self.custom_headers = {
            'Host': 'stats.nba.com',
            'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/111.0.0.0 Safari/537.36'),
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'x-nba-stats-origin': 'stats',
            'x-nba-stats-token': 'true',
            'Connection': 'keep-alive',
            'Referer': 'https://stats.nba.com/',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache'
        }

    def get_last_finished_games(self):
        """Return the last games finished within the last 10 days"""
        game_list = []
        for offset in range(0, -10, -1):
            scoreboard = Scoreboard(day_offset=offset, headers=self.custom_headers)
            games = scoreboard.get_normalized_dict().get('GameHeader')
            for game in games:
                # pprint(game)
                if game.get('GAME_STATUS_ID') != 3:
                    continue
                game_list.append(game)
            if len(game_list) > 0:
                break
        return game_list

    def get_game_list_details(self, game_list):
        # retrieve game stats
        games = []
        for game in game_list:
            sleep(1)
            games.append(self.get_game_details(game))
        return games

    def get_game_details(self, game):
        """provides details of the given game id"""
        game_id = game.get('GAME_ID')
        score = BoxScoreTraditionalV2(game_id=game_id, headers=self.custom_headers)
        home_team = teams.find_team_name_by_id(game['HOME_TEAM_ID'])
        visitor_team = teams.find_team_name_by_id(game['VISITOR_TEAM_ID'])
        return {'basic_info': game, 'home_team': home_team, 'visitor_team': visitor_team,
                'stats': score.get_normalized_dict()}

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
        if stat == 0:
            return ""
        if stat == 1:
            return f" 1 {singular_name}."
        else:
            return f" {stat} {singular_name}s."

    def create_player_summary(self, player):
        player_name = player['PLAYER_NAME']
        nick = player['NICKNAME']
        minutes_played = self.normalize_time(player['MIN'])

        comment = player['COMMENT']
        points = self.normalize_number(player['PTS'])
        rebounds = self.normalize_number(player['REB'])
        assists = self.normalize_number(player['AST'])
        steals = self.normalize_number(player['STL'])
        turnovers = self.normalize_number(player['TO'])

        if minutes_played is None:
            return f"\t{player_name} ({nick}) didn't play ({comment})."
        text = (f"\t{player_name} ({nick}) played {minutes_played} minutes, "
                f"scored {points} points, caught {rebounds} rebounds and made {assists} assists.")
        # only add these stats if not zero
        text += self.pluralize(steals, "steal")
        text += self.pluralize(turnovers, "turnover")
        return text

    def create_players_summary(self, team, player_stats):
        """
        Generate a text-based summary of all players performances in a game
        from the given team
        """
        summary = ""
        for player in player_stats:
            if player['TEAM_ID'] != team['id']:
                continue
            summary += self.create_player_summary(player)
            summary += '\n'
        return summary

    def create_team_summary(self, team_stats, team_id):
        """
        return the points and a text description of the given team_id from the list
        of team results.
        """
        # find the matching team from the list
        team = list(filter(lambda x: x['TEAM_ID'] == team_id, team_stats))[0]

        # get properties
        team_name = team['TEAM_NAME']
        points = self.normalize_number(team['PTS'])
        rebounds = self.normalize_number(team['REB'])
        assists = self.normalize_number(team['AST'])
        steals = self.normalize_number(team['STL'])
        turnovers = self.normalize_number(team['TO'])
        return (points,
                (f"{team_name} scored {points} points, got {rebounds} rebounds, "
                 f"did {assists} assists and {steals} steals. Game turnovers: {turnovers}."))

    def create_game_summary(self, game):
        """Generate a human-readable text summary for a given game"""
        visitor_team = game['visitor_team']['full_name']
        visitor_points, visitor_team_summary = self.create_team_summary(game['stats']['TeamStats'],
                                                                        game['visitor_team']['id'])
        visitor_players_summary = self.create_players_summary(game['visitor_team'],
                                                              game['stats']['PlayerStats'])

        game_location = f"{game['home_team']['city']}, {game['home_team']['state']}"
        home_team = game['home_team']['full_name']
        home_points, home_team_summary = self.create_team_summary(game['stats']['TeamStats'],
                                                                  game['home_team']['id'])
        home_players_summary = self.create_players_summary(game['home_team'],
                                                           game['stats']['PlayerStats'])

        text = f"""
The final score was:

{visitor_team} {visitor_points} - {home_points} {home_team}

The game was played in {game_location}.

{visitor_team_summary}
{home_team_summary}

{home_team} played with the following players:
{home_players_summary}
{visitor_team} played with the following players:
{visitor_players_summary}"""
        return text

    def print_game_data(self, game):
        home_pts, _ = self.create_team_summary(game['stats']['TeamStats'], game['home_team']['id'])
        home_team = game['home_team']['full_name']
        visitor_team = game['visitor_team']['full_name']
        visitor_pts, _ = self.create_team_summary(game['stats']['TeamStats'], game['visitor_team']['id'])

        return (f"{visitor_team} **{visitor_pts}** - "
                f"**{home_pts}** {home_team}\n")

    def get_standings(self, conference):
        """return the list of standings of both conferences"""
        scoreboard = Scoreboard(headers=self.custom_headers)
        standings = scoreboard.get_normalized_dict()

        self.standings = {'east': standings.get('EastConfStandingsByDay'),
                          'west': standings.get('WestConfStandingsByDay')}

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
