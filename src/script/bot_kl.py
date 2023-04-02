import os

from pprint import pprint
from ai import ai
from twitter import twitter
from kl_prompts import basic_prompts


def main():
    """
    Get the list of last day games, generate a prompt,
    pass it to openai and twit all of them
    """
    twitterer = twitter()
    twitterer.authenticate()

    print(basic_prompts)
    kl_ai = ai(basic_prompts=basic_prompts)

    custom_prompt = input("Introduce el tema de la Kings League: ")
    tweets = kl_ai.generate_text_from_chat(custom_prompt=custom_prompt)
    print()
    print(tweets)
    response = twitterer.create_thread(tweets)
    print(f"https://twitter.com/estaPasandoKL/status/{response.data['id']}")


if __name__ == "__main__":
    main()
