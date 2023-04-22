from datetime import datetime
from time import sleep
from urllib.request import urlopen, urlparse, Request
from urllib.error import URLError, HTTPError, ContentTooShortError

from bs4 import BeautifulSoup

import source
from sources.espn_stats import espn_stats

class espn_recap:
    """reads Kings-league related news and generates prompts with those"""

    nba_url = "http://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
    nba_news_prefix = 'https://www.espn.com/nba/recap'
    method_name = 'espn_recap'
    prompt_max_length = 4000
    
    def __init__(self):
        self.espn = espn_stats(return_format='full_event')

    def get_sources(self):
        """
        Get a list of kings leage related news with url as the id. Returns a
        list of non-duplicate source objects
        """
        games = self.espn.get_last_finished_games()
        sources = []
        for game in games:
            for link in game['links']:
                if link['text'] == 'Recap':
                    sources.append(source.source(id=link['href'], method=self.method_name, date=datetime.now()))
        return sources

    def generate_prompt(self, s):
        """
        Given a news shource s, with at least an id (url), return a string with a text prompt
        """
        try:
            html = urlopen(Request(s.id))
        except (URLError, HTTPError, ContentTooShortError) as e:
            print(e)
            return None
        sleep(1)  # artificial wait to prevent getting banned from the website
        soap = BeautifulSoup(html, 'html.parser')
        h1 = soap.find('h1')
        if h1 is None:
            return None
        title = h1.text.strip()
        subtitle = ""
        article = soap.find('div', class_='Story__Body')
        paragraphs = []
        if article is not None:
            paragraphs = article.findAll('p')
        body = ""
        if paragraphs is not None:
            header_length = len(title) + len(subtitle) + 6
            for p in paragraphs:
                text = p.text.strip()
                if (header_length + len(body) + len(text)) > self.prompt_max_length:
                    break
                body += ("\n\n " + text)
        prompt = f"React to the following game recap:\n\n{title}\n\n{subtitle}\n\n{body}"
        return prompt
