from ai import ai
from twitter import twitter
from prompts.nba_prompts import basic_prompts
import source

def main():
    """
    Get the list of last day games, generate a prompt,
    pass it to openai and twit all of them
    """
    twitterer = twitter()
    twitterer.authenticate()

    # get list of last day finished games
    games = source.source.read_sources('espn_stats')
    
    nba_ai = ai(basic_prompts=basic_prompts)

    # for each game, send a tweet
    for game in games:
        print(game.id)
        game_summary = game.get_prompt()
        #print(game_summary)
        tweets = nba_ai.generate_text_from_chat(custom_prompt=game_summary)
        print()
        print(tweets)
        #twitterer.create_thread(tweets)


if __name__ == "__main__":
    main()
