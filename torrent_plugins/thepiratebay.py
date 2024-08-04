import urllib.parse
import json
import requests
from prettyprinter import pprint


class thepiratebay:
    url = 'https://thepiratebay.org'
    api = 'https://apibay.org'
    name = 'The Pirate Bay w. categories'

    supported_categories = {
        'all': [0],
        'anime': [
            207, 208, 201, 202, 205, 206, 209, 299, 501, 502, 505, 599, 699
        ],
        'books': [601, 602],
        'games': [400, 504],
        'movies': [207],
        'music': [101, 104],
        'pictures': [603, 604, 503],
        'software': [300],
        'tv': [208]
    }

    torrent = '{self.url}/description.php?id={id}'
    download = '{self.api}/t.php?id={id}'
    magnet = 'magnet:?xt=urn:btih:{hash}&dn={name}&{trackers} {info}'
    query = '{self.api}/q.php?q={what}&cat={category}'

    trackers = [
        'udp://tracker.coppersurfer.tk:6969/announce',
        'udp://tracker.openbittorrent.com:6969/announce',
        'udp://9.rarbg.to:2710/announce',
        'udp://9.rarbg.me:2780/announce',
        'udp://9.rarbg.to:2730/announce',
        'udp://tracker.opentrackr.org:1337',
        'http://p4p.arenabg.com:1337/announce',
        'udp://tracker.torrent.eu.org:451/announce',
        'udp://tracker.tiny-vps.com:6969/announce',
        'udp://open.stealth.si:80/announce'
    ]

    def retrieve_url(self, url, proxy_server_address):
        # Make a request to the URL and return the response, but use the proxy server address
        response = requests.get(url, proxies={"http": proxy_server_address})
        return response.text

    def get_magnet_link(self, data):
        name = urllib.parse.quote(data['name'], safe='')
        trs = urllib.parse.urlencode({'tr': self.trackers}, True)
        return self.magnet.format(hash=data['info_hash'], name=name, trackers=trs, info='')

    def search_and_yield(self, what, cat='all', proxy_server_address=None, magnets_to_yield=10):
        # If no proxy server address is provided, return an error
        if proxy_server_address is None:
            print("No proxy server address provided, skipping search")
            return
        result_count = 0
        for category in self.supported_categories[cat]:
            url = self.query.format(self=self, what=what, category=category)
            response = json.loads(self.retrieve_url(url, proxy_server_address))

            for torrent in response:
                if torrent['name'] == "No results returned":
                    break
                torrent_id = self.torrent.format(self=self, id=torrent['id'])
                data = {
                    'name': torrent['name'],
                    'size': torrent['size'],
                    'seeders': torrent['seeders'],
                    'leechers': torrent['leechers'],
                    'magnet': self.get_magnet_link(torrent),
                    'source': "The Pirate Bay"
                }
                print(f'Found: {data["name"]}, Source: {data["source"]}')
                yield data
                result_count += 1
                if result_count >= magnets_to_yield:
                    return
