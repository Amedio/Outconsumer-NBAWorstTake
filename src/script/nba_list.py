from ai import ai
from sources.espn_stats import espn_stats
from twitter import twitter
from prompts.nba_prompts import basic_prompts


def main():
    """
    Get the list of last day games, generate a prompt,
    pass it to openai and twit all of them
    """
    twitterer = twitter()
    twitterer.authenticate()

    # get list of last day finished games
    nba = espn_stats()
    game_list = nba.get_last_finished_games()
    game_stats = nba.get_game_list_details(game_list)

    nba_ai = ai(basic_prompts=basic_prompts)

    # for each game, send a tweet
    for game in game_stats:
        #pprint(game)
        game_summary = nba.create_game_summary(game)
        tweets = nba_ai.generate_text_from_chat(custom_prompt=game_summary)
        print()
        print(tweets)
        #twitterer.create_thread(tweets)


if __name__ == "__main__":
    main()
