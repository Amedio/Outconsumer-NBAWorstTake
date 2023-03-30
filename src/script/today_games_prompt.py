
from nba_api.stats.endpoints import Scoreboard, BoxScoreTraditionalV2
import datetime
import math




def game_to_prompt():
    return ""


def player_stats_to_prompt(player):
    prompt = " \t "
    prompt += player[1]['PLAYER_NAME']


    min = player[1]['MIN']
    if min != None:
        prompt += f" played {min} minutes"
    else:
        prompt += f" not played ({player[1]['COMMENT']}) \n"
        return prompt

    points = player[1]['PTS']
    if not(math.isnan(points)):
        prompt += f" with {math.floor(player[1]['PTS'])} points" 
    else:
        prompt += " with 0 points"

    rebounds = player[1]['REB']
    if not(math.isnan(rebounds)):
        prompt += f" and {math.floor(player[1]['REB'])} rebounds " 
    else:
        " "
    return "    " + prompt + "\n"


def get_today_games(): 
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    yesterday_date = yesterday.strftime('%m/%d/%Y')

    scoreboard = Scoreboard(day_offset=0, game_date=yesterday_date)
    return scoreboard



def request_prompt():
    return "Make an analyisis of the following game.In the style of a twitter dude and in less than 280 characters. talk in low IQ and make stupid assumptions don't point out more than 3 numerical stats. dont use a lot of number stats."


if __name__ == "__main__":

    games = get_today_games()

    score_line = games.line_score.get_data_frame()

    scorebox = games.game_header.get_data_frame()

    for i, game in scorebox.iterrows():


        prompt = request_prompt()

        prompt += f"\n Final score: {score_line.iloc[i*2]['TEAM_CITY_NAME']}  {score_line.iloc[i*2]['PTS']} - {score_line.iloc[(i*2) + 1]['PTS']} {score_line.iloc[(i*2) + 1]['TEAM_CITY_NAME']}."


        scoreboard =  BoxScoreTraditionalV2(game['GAME_ID'])
        home_team = scoreboard.data_sets[0].get_data_frame()
  


        f_team = score_line.iloc[i*2]['TEAM_CITY_NAME']
        for player in home_team.iterrows():


            if player[0] == 0:
                prompt += f" \n \n {f_team} played with the following players: \n \n"

            if(player[1]["TEAM_CITY"] != f_team):
                f_team = score_line.iloc[(i*2) + 1]['TEAM_CITY_NAME']
                prompt += f"  \n \n    {f_team} played with the following players: \n \n"
         

            team = player[1]["TEAM_CITY"]
            prompt += player_stats_to_prompt(player)
        prompt += ""
        print(f"\n {prompt} \n")

      