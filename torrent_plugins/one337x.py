import urllib.parse
import json
import requests
import re
from html.parser import HTMLParser
from prettyprinter import pprint


class one337x:
    url = 'https://1337x.to'
    name = '1337x'
    supported_categories = {
        'all': None,
        'anime': 'Anime',
        'software': 'Apps',
        'games': 'Games',
        'movies': 'Movies',
        'music': 'Music',
        'tv': 'TV',
    }

    class MyHtmlParser(HTMLParser):

        def error(self, message):
            pass

        A, TD, TR, HREF, TBODY, TABLE = ('a', 'td', 'tr', 'href', 'tbody', 'table')

        def __init__(self, url):
            HTMLParser.__init__(self)
            self.url = url
            self.row = {}
            self.column = None
            self.insideRow = False
            self.foundTable = False
            self.foundResults = False
            self.parser_class = {
                'name': 'name',
                'seeds': 'seeds',
                'leech': 'leeches',
                'size': 'size'
            }
            self.results = []

        def handle_starttag(self, tag, attrs):
            params = dict(attrs)
            if 'search-page' in params.get('class', ''):
                self.foundResults = True
                return
            if self.foundResults and tag == self.TBODY:
                self.foundTable = True
                return
            if self.foundTable and tag == self.TR:
                self.insideRow = True
                return
            if self.insideRow and tag == self.TD:
                classList = params.get('class', None)
                for columnName, classValue in self.parser_class.items():
                    if classValue in classList:
                        self.column = columnName
                        self.row[self.column] = -1
                return

            if self.insideRow and tag == self.A:
                if self.column != 'name' or self.HREF not in params:
                    return
                link = params[self.HREF]
                if link.startswith('/torrent/'):
                    link = f'{self.url}{link}'
                    torrent_page = requests.get(link).text
                    magnet_regex = r'href="magnet:.*"'
                    matches = re.finditer(magnet_regex, torrent_page, re.MULTILINE)
                    magnet_urls = [x.group() for x in matches]
                    self.row['link'] = magnet_urls[0].split('"')[1]
                    self.row['engine_url'] = self.url
                    self.row['desc_link'] = link

        def handle_data(self, data):
            if self.insideRow and self.column:
                if self.column == 'size':
                    data = data.replace(',', '')
                self.row[self.column] = data
                self.column = None

        def handle_endtag(self, tag):
            if tag == self.TABLE:
                self.foundTable = False
            if self.insideRow and tag == self.TR:
                self.insideRow = False
                self.column = None
                if not self.row:
                    return
                self.results.append(self.row)
                self.row = {}

    def retrieve_url(self, url, proxy_server_address):
        response = requests.get(url, proxies={"http": proxy_server_address})
        return response.text

    def search_and_yield(self, what, cat='all', proxy_server_address=None, magnets_to_yield=10):
        if proxy_server_address is None:
            return
        parser = self.MyHtmlParser(self.url)
        what = what.replace('%20', '+')
        category = self.supported_categories[cat]
        page = 1
        result_count = 0

        while result_count < magnets_to_yield:
            page_url = f'{self.url}/category-search/{what}/{category}/{page}/' if category else f'{self.url}/search/{what}/{page}/'
            html = self.retrieve_url(page_url, proxy_server_address)
            parser.feed(html)
            if html.find('<li class="last">') == -1:
                # exists on every page but the last
                break
            for result in parser.results:
                if result_count >= magnets_to_yield:
                    break
                print(f"Found {result['name']}, Source: 1337x")
                yield {
                    'name': result['name'],
                    'size': result['size'],
                    'seeders': result['seeds'],
                    'leechers': result['leech'],
                    'magnet': result['link'],
                    'source' : "1337x"
                }
                result_count += 1
            parser.results.clear()
            page += 1

        parser.close()
