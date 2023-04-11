from datetime import datetime
from time import sleep
from urllib.request import urlopen, urlparse, Request
from urllib.error import URLError

from bs4 import BeautifulSoup

import source


class as_news:
    """reads Kings-league related news and generates prompts with those"""

    kl_url = "https://esports.as.com/bonus/kings-league/"
    kl_news_prefix = 'https://esports.as.com/bonus/kings-league/'
    method_name = 'as'
    prompt_max_length = 4000

    def get_sources(self):
        """
        Get a list of kings leage related news with url as the id. Returns a
        list of non-duplicate source objects
        """
        html = urlopen(Request(self.kl_url))
        sleep(1)  # artificial wait to prevent getting banned from the website
        soap = BeautifulSoup(html, 'html.parser')
        links = []
        for h2 in soap.select('h2'):
            for a in h2.select('a'):
                link = a.get("href")
                if link.startswith('/'):
                    url = urlparse(self.kl_url)
                    link = url.scheme + '://' + url.netloc + link
                if link.startswith(self.kl_news_prefix) and link not in links:
                    links.append(link)
        sources = []
        for link in links:
            sources.append(source.source(id=link, method=self.method_name, date=datetime.now()))
        return sources

    def generate_prompt(self, s):
        """
        Given a news shource s, with at least an id (url), return a string with a text prompt
        """
        html = urlopen(Request(s.id))
        sleep(1)  # artificial wait to prevent getting banned from the website
        soap = BeautifulSoup(html, 'html.parser')
        title = soap.find('h1').text.strip()
        subtitle = soap.find('h2').text.strip()
        article = soap.find('div', class_='mce-body')
        paragraphs = []
        if article is not None:
            paragraphs = article.findAll('p')
        body = ""
        if paragraphs is not None:
            header_length = len(title) + len(subtitle) + 6
            for p in paragraphs:
                text = p.text.strip()
                if (header_length + len(body) + len(text)) > prompt_max_length:
                    break
                body += ("\n\n " + text)
        prompt = f"Reacciona a la siguiente noticia:\n\n{title}\n\n{subtitle}\n\n{body}"
        return prompt
