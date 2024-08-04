import math
import re
import requests
import urllib.parse
from html.parser import HTMLParser
from prettyprinter import pprint

class torrentgalaxy:
    url = 'https://torrentgalaxy.to/'
    name = 'TorrentGalaxy'
    supported_categories = {
        'all': '',
        'movies': 'c3=1&c46=1&c45=1&c42=1&c4=1&c1=1&',
        'tv': 'c41=1&c5=1&c6=1&c7=1&',
        'music': 'c23=1&c24=1&c25=1&c26=1&c17=1&',
        'games': 'c43=1&c10=1&',
        'anime': 'c28=1&',
        'software': 'c20=1&c21=1&c18=1&',
        'pictures': 'c37=1&',
        'books': 'c13=1&c19=1&c12=1&c14=1&c15=1&',
    }

    class TorrentGalaxyParser(HTMLParser):
        DIV, A, SPAN, FONT, SMALL = 'div', 'a', 'span', 'font', 'small'
        count_div = -1
        get_size, get_seeds, get_leechs = False, False, False

        def __init__(self, url):
            super().__init__()
            self.url = url
            self.this_record = {}
            self.results = []

        def handle_starttag(self, tag, attrs):
            if tag == self.DIV:
                my_attrs = dict(attrs)
                if my_attrs.get('class') and 'tgxtablerow' in my_attrs.get('class'):
                    self.count_div = 0
                    self.this_record = {}
                    self.this_record['engine_url'] = self.url
                if my_attrs.get('class') and 'tgxtablecell' in my_attrs.get('class') and self.count_div >= 0:
                    self.count_div += 1

            if tag == self.A and self.count_div < 13:
                my_attrs = dict(attrs)
                if 'title' in my_attrs and 'class' in my_attrs and 'txlight' in my_attrs.get('class') and not my_attrs.get('id'):
                    self.this_record['name'] = my_attrs['title']
                    self.this_record['desc_link'] = self.url + my_attrs['href']
                if 'role' in my_attrs and my_attrs.get('role') == 'button':
                    self.this_record['link'] = my_attrs['href']

            if tag == self.SPAN:
                my_attrs = dict(attrs)
                if 'class' in my_attrs and 'badge badge-secondary' in my_attrs.get('class'):
                    self.get_size = True

            if tag == self.FONT:
                my_attrs = dict(attrs)
                if my_attrs.get('color') == 'green':
                    self.get_seeds = True
                elif my_attrs.get('color') == '#ff0000':
                    self.get_leechs = True

            if self.count_div == 13 and tag == self.SMALL:
                self.results.append(self.this_record)
                self.this_record = {}
                self.count_div = -1

        def handle_data(self, data):
            if self.get_size and self.count_div < 13:
                self.this_record['size'] = data.strip().replace(',', '')
                self.get_size = False
            if self.get_seeds:
                self.this_record['seeds'] = data.strip().replace(',', '')
                self.get_seeds = False
            if self.get_leechs:
                self.this_record['leech'] = data.strip().replace(',', '')
                self.get_leechs = False

        def get_results(self):
            return self.results

    def retrieve_url(self, url, proxy_server_address):
        response = requests.get(url, proxies={"http": proxy_server_address})
        return response.text

    def search_and_yield(self, what, cat='all', proxy_server_address=None, magnets_to_yield=10):
        if proxy_server_address is None:
            return
        parser = self.TorrentGalaxyParser(self.url)
        what = urllib.parse.quote(what)
        result_count = 0

        search_url = 'https://torrentgalaxy.to/torrents.php?'
        full_url = search_url + self.supported_categories[cat.lower()] + 'sort=seeders&order=desc&search=' + what
        retrieved_html = self.retrieve_url(full_url, proxy_server_address)
        parser.feed(retrieved_html)

        all_results_re = re.compile(r'steelblue[^>]+>(.*?)<')
        if len(all_results_re.findall(retrieved_html)) == 0:
            return
        all_results = all_results_re.findall(retrieved_html)[0]
        all_results = all_results.replace(' ', '')
        pages = math.ceil(int(all_results) / 50)

        for page in range(1, pages + 1):
            if result_count >= magnets_to_yield:
                break
            page_url = full_url + '&page=' + str(page)
            retrieved_html = self.retrieve_url(page_url, proxy_server_address)
            parser.feed(retrieved_html)
            results = parser.get_results()
            parser.results.clear()

            if not results:
                break

            for result in results:
                if result_count >= magnets_to_yield:
                    break
                yield {
                    'name': result['name'],
                    'size': result['size'],
                    'seeders': result['seeds'],
                    'leechers': result['leech'],
                    'magnet': result['link']
                }
                result_count += 1

        parser.close()
