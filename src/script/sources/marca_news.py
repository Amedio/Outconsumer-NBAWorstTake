from datetime import datetime
from time import sleep
from urllib.request import urlopen, Request
from urllib.error import URLError

from bs4 import BeautifulSoup

import source


class marca_news():
    """reads Kings-league related news and generates prompts with those"""

    kl_url = "https://www.marca.com/videojuegos/kings-league.html"
    kl_news_prefix = 'https://www.marca.com/videojuegos/kings-league/'
    method_name = 'marca'
    prompt_max_length = 4000

    def get_sources(self):
        """
        Get a list of kings leage related news with url as the id. Returns a list of non-duplicate
        source objects
        """
        html = urlopen(Request(self.kl_url))
        sleep(1)  # artificial wait to prevent getting banned from the website
        soap = BeautifulSoup(html, 'html.parser')
        links = []
        for h2 in soap.select('h2'):
            link = h2.parent.get('href')
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
        #paragraphs = soap.findAll('p', {'data-mrf-recirculation': "Links Párrafos"})
        paragraphs = soap.find('article').findAll('p')
        body = ""
        if paragraphs is not None:
            header_length = len(title) + len(subtitle) + 6
            for p in paragraphs:
                text = p.text.strip()
                if 'MARCA' in p.text or 'fantasy' in p.text.lower():  # skip MARCA promotions
                    continue
                if (header_length + len(body) + len(text)) > self.prompt_max_length:
                    break
                body += ("\n\n " + text)
        prompt = f"Reacciona a la siguiente noticia:\n\n{title}\n\n{body}"
        return prompt