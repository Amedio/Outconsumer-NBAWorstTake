from ai import ai
import sources.espn_recap
from twitter import twitter
from prompts.nba_prompts import basic_prompts
#from pprint import pprint

def main():
    """
    Get the list of last day games, generate a prompt,
    pass it to openai and twit all of them
    """
    twitterer = twitter()
    twitterer.authenticate()

    # get list of last day finished games
    nba = sources.espn_recap.espn_recap()
    game_recaps = nba.get_sources()
    
    nba_ai = ai(basic_prompts=basic_prompts)

    # for each game, send a tweet
    for game in game_recaps:
        print(game.id)
        game_summary = nba.generate_prompt(game)
        #print(game_summary)
        tweets = nba_ai.generate_text_from_chat(custom_prompt=game_summary)
        print()
        print(tweets)
        #twitterer.create_thread(tweets)


if __name__ == "__main__":
    main()
