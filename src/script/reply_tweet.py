import re
import sys

import snscrape.modules.twitter as sntwitter

from ai import ai
import twitter
import prompts.kl_prompts
import prompts.nba_prompts


def reply_tweet(type, tweet):
    # setup twitter
    twitterer = twitter.twitter()

    # setup AI
    if type == 'nba':  # TODO: get basic_prompts and config from db
        basic_prompts = prompts.nba_prompts.basic_prompts
        twitter_account = "TheNBAWorstTake"
    else:
        basic_prompts = prompts.kl_prompts.basic_prompts
        twitter_account = "estaPasandoKL"
    my_ai = ai(basic_prompts=basic_prompts)

    # get tweet
    response = re.search(r'[0-9]+', str(tweet))
    if response is None:
        print("Tweet id not found", file=sys.stderr)
        sys.exit(1)
    original_tweet_id = response.group(0)

    prompt = None
    for original_tweet in sntwitter.TwitterTweetScraper(tweetId=original_tweet_id).get_items():
        tweet_text = original_tweet.rawContent
        tweet_author = original_tweet.user.username
        prompt = f"Responde al siguiente tweet, referenciando al autor (@{tweet_author}):\n\n{tweet_text}"
        break
    print(prompt)

    # call AI
    tweets = my_ai.generate_text_from_chat(custom_prompt=prompt)

    # tweet text
    print(f"Sending tweets: {tweets}")

    response = twitterer.create_thread(tweets, in_replay_to=original_tweet_id)
    tweet_id = response.data['id']
    print(f"https://twitter.com/{twitter_account}/status/{tweet_id}")
    if len(response.errors) > 0:
        print(response.errors)

def main():
    if len(sys.argv) != 3:
        print("replying to a tweet requires 2 compulsory parameters: the type of bot (kings_league or nba) and the tweet url or id", file=sys.stderr)
        sys.exit(1)
    reply_tweet(sys.argv[1], sys.argv[2])


if __name__ == "__main__":
    main()
