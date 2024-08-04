import math
import re
import urllib.parse
import requests
from html.parser import HTMLParser
from prettyprinter import pprint

class bitsearch:
    url = 'https://bitsearch.to'
    name = 'Bit Search'
    supported_categories = {
        'all': 'all'
    }
    
    results_regex = r'<b>\d+<\/b>'

    class MyHtmlParser(HTMLParser):
    
        def error(self, message):
            pass
    
        LI, DIV, H5, A = ('li', 'div', 'h5', 'a')
    
        def __init__(self, url):
            HTMLParser.__init__(self)
            self.magnet_regex = r'href=["\']magnet:.+?["\']'

            self.url = url
            self.row = {}

            self.column = 0

            self.insideSearchResult = False
            self.insideInfoDiv = False
            self.insideName = False
            self.shouldGetName = False
            self.insideStatsDiv = False
            self.insideStatsColumn = False
            self.insideLinksDiv = False
            self.isValidInfo = False
            self.results = []

        def handle_starttag(self, tag, attrs):
            params = dict(attrs)
            cssClasses = params.get('class', '')

            if tag == self.LI and 'search-result' in cssClasses:
                self.insideSearchResult = True
                return

            if self.insideSearchResult and tag == self.DIV and self.is_search_result(cssClasses):
                self.insideInfoDiv = True
                self.isValidInfo = True
                return

            if self.isValidInfo:
                if self.insideInfoDiv and tag == self.H5:
                    self.insideName = True
                    return

                if self.insideName and tag == self.A:
                    self.shouldGetName = True
                    href = params.get('href')
                    link = f'{self.url}{href}'
                    self.row['desc_link'] = link
                    return

                if self.insideSearchResult and tag == self.DIV and 'stats' in cssClasses:
                    self.insideStatsDiv = True
                    return

                if self.insideStatsDiv and tag == self.DIV:
                    self.insideStatsColumn = True
                    self.column += 1
                    return

                if self.insideSearchResult and tag == self.DIV and 'links' in cssClasses:
                    self.insideLinksDiv = True
                    return

                if self.insideLinksDiv and tag == self.A and 'dl-magnet' in cssClasses:
                    href = params.get('href')
                    self.row['link'] = href
                    self.insideLinksDiv = False
                    return

        def handle_data(self, data):
            if self.shouldGetName:
                self.row['name'] = data.strip()
                self.shouldGetName = False
                return

            if self.insideStatsDiv:
                if not data.rstrip() == '':                  
                    if self.column == 2:
                        self.row['size'] = data.replace(' ', '')
                    if self.column == 3: 
                        self.row['seeds'] = data
                    if self.column == 4: 
                        self.row['leech'] = data
                return

        def handle_endtag(self, tag):
            if tag == self.H5 and self.insideName:
                self.insideName = False
                return

            if self.insideStatsDiv and not self.insideStatsColumn:
                self.insideStatsDiv = False
                self.insideInfoDiv = False
                return

            if self.insideStatsColumn and tag == self.DIV:
                self.insideStatsColumn = False
                return

            if tag == self.LI and self.insideSearchResult:
                self.row['engine_url'] = self.url
                if self.isValidInfo:
                    self.results.append(self.row)
                self.insideSearchResult = False
                self.column = 0
                self.row = {}
                return

        def is_search_result(self, classes):
            return 'info' in classes and 'px-3' in classes

    def retrieve_url(self, url, proxy_server_address):
        response = requests.get(url, proxies={"http": proxy_server_address})
        return response.text

    def search_and_yield(self, what, cat='all', proxy_server_address=None, magnets_to_yield=10):
        if proxy_server_address is None:
            return
        parser = self.MyHtmlParser(self.url)
        what = what.replace('%20', '+')
        what = what.replace(' ', '+')
        page = 1
        result_count = 0

        while result_count < magnets_to_yield:
            page_url = f'{self.url}/search?q={what}&page={page}'
            retrieved_html = self.retrieve_url(page_url, proxy_server_address)
            results_matches = re.finditer(self.results_regex, retrieved_html, re.MULTILINE)
            results_array = [x.group() for x in results_matches]
    
            if len(results_array) > 0:
                results = int(results_array[0].replace('<b>', '').replace('</b>', ''))
                pages = math.ceil(results / 20)
            else:
                pages = 0

            page += 1

            if pages > 0:
                parser.feed(retrieved_html)

                while page <= pages:
                    page_url = f'{self.url}/search?q={what}&page={page}'
                    retrieved_html = self.retrieve_url(page_url, proxy_server_address)
                    parser.feed(retrieved_html)
                    for result in parser.results:
                        if result_count >= magnets_to_yield:
                            break
                        yield {
                            'name': result['name'],
                            'size': result['size'],
                            'seeders': result['seeds'],
                            'leechers': result['leech'],
                            'magnet': result['link'],
                            'source' : "Bit Search"
                        }
                        result_count += 1
                    parser.results.clear()
                    page += 1

            if result_count >= magnets_to_yield:
                break

        parser.close()
