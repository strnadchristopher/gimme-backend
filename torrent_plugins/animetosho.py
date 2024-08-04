from html.parser import HTMLParser
import requests
import urllib.parse

class animetosho:
    url = "https://animetosho.org"
    name = "Anime Tosho"
    supported_categories = {
        "all": [""]
    }

    def retrieve_url(self, url, proxy):
        response = requests.get(url, proxies={"http": proxy, "https": proxy})
        return response.text

    def search_and_yield(self, what, cat='all', proxy=None, magnets_to_yield=10):
        results_count = 0
        for page in range(1, 10):
            url = f"https://animetosho.org/search?q={what}&page={page}"
            try:
                html = self.retrieve_url(url, proxy)
                parser = self.DataExtractor()
                parser.feed(html)
                results = parser.get_results()
                if len(results) == 0:
                    break
            except Exception as e:
                print(f"Error fetching data from Anime Tosho: {e}")
                break
            for result in results:
                yield result
                results_count += 1
                if results_count >= magnets_to_yield:
                    return

    class DataExtractor(HTMLParser):
        def __init__(self):
            super().__init__()
            self.in_correct_tag = False
            self.found_size = False
            self.found_name = False
            self.save_name_data = False
            self.look_for_magnet = False
            self.look_for_seeds = False
            self.results = []
            self.current_result = {"engine_url": "https://animetosho.org/"}

        def handle_starttag(self, tag, attrs):
            for attr in attrs:
                attribute = attr[0]
                attribute_values = attr[1].split()
                if attribute == 'class' and "home_list_entry" in attribute_values and "home_list_entry_compl_1" in attribute_values:
                    self.in_correct_tag = True

                if self.in_correct_tag:
                    if attribute == 'class' and "size" in attribute_values:
                        self.found_size = True

                    if self.found_size:
                        if attribute == 'title':
                            size = attribute_values[3].replace(",", "")
                            self.current_result["size"] = size
                            self.found_size = False

                    if attribute == 'class' and "link" in attribute_values:
                        self.found_name = True

                    if self.found_name:
                        if tag == "a":
                            description = attribute_values[0]
                            self.current_result["desc_link"] = description
                            self.save_name_data = True
                            self.found_name = False

                    if attribute == 'class' and "links" in attribute_values:
                        self.look_for_magnet = True
                        self.look_for_seeds = True

                    if self.look_for_magnet:
                        if tag == "a":
                            if attribute_values[0].startswith("magnet:?xt"):
                                self.current_result["link"] = attribute_values[0]
                                self.look_for_magnet = False

                    if self.look_for_seeds:
                        if tag == "span":
                            if attribute == "title":
                                seeds, leech = attr[1].split("/")
                                seeds = seeds.split(": ")[1].strip()
                                leech = leech.split(": ")[1].strip()
                                self.current_result["seeders"] = seeds
                                self.current_result["leechers"] = leech
                    self.current_result["source"] = "Anime Tosho"

                    self.check_current_result_completed()

        def handle_data(self, data):
            if self.save_name_data:
                self.current_result["name"] = data
                self.save_name_data = False

        def check_current_result_completed(self):
            if 'name' in self.current_result and 'link' in self.current_result:
                self.results.append(self.current_result)
                self.current_result = {"engine_url": "https://animetosho.org/"}
                self.in_correct_tag = False

        def get_results(self):
            return self.results

if __name__ == "__main__":
    a = animetosho()
    for result in a.search_and_yield("zom+judas"):
        print(result)
