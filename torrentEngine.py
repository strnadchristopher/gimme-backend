from selenium import webdriver
from selenium.webdriver.common.by import By
import asyncio
import time
from qbittorrentapi import Client, TorrentState
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--headless')
driver = webdriver.Chrome(options=chrome_options)
driver.implicitly_wait(10)
QUALITY_4K = "211"
QUALITY_1080P = "207"

def get_torrents_info(client):
    currently_downloading = []
    queued_to_download = []
    # We're gonna create the status message, which should always list first the movies that are currently downloading, and then the movies that are queued to download, we'll use equal signs to separate the two
    for torrent in client.torrents_info():
        state_enum = TorrentState(torrent.state)
        # We get the name of the torrent, by calling client.torrents_properties(torrent.hash), it will return a "save_path" key, which is the path to the torrent, remove any path before the last / or \ to get the torrent name
        torrent_name = client.torrents_properties(torrent.hash)["name"]
        # List all key and values in client.torrents_properties(torrent.hash) for debugging
        # print(client.torrents_properties(torrent.hash))
        if torrent.state_enum.is_downloading:
            torrent_properties = client.torrents_properties(torrent.hash)
            if state_enum.value == "queuedDL" or state_enum.value == "pausedDL":
                queued_to_download.append(torrent_properties)
            else:
                # We need to convert torrent_eta to a human readable format, its in milliseconds and should be converted to hours, minutes, seconds
                currently_downloading.append(torrent_properties)
    # Sort queued_to_download by priority, which is it's 
    print("==========================", flush=True)
    for torrent in currently_downloading:
        print("Currently downloading: " + torrent["name"] +
              " ETA: " + str(time.strftime('%H:%M:%S', time.gmtime(torrent["eta"]))), flush=True)
    print("==========================", flush=True)
    for torrent in queued_to_download:
        print("Queued to download: " + torrent["name"], flush=True)
    print("\n\n", flush=True)
    return {"currently_downloading": currently_downloading, "queued_to_download": queued_to_download}


def search_for_movie(movie_title, client=None):
    # We need to pause all the torrents before we start searching for a new movie, as our platform cannot handle doing both for some reason
    # paused_torrents = []
    # if client is not None:
    #     for torrent in client.torrents_info():
    #         client.torrents_pause(torrent.hash)
    #         paused_torrents.append(torrent.hash)
    
    # Sleep for 5 seconds so the torrents can pause
    time.sleep(5)
            
    # We need to url encode the movie title, meaning we replace spaces with + signs
    import urllib.parse
    
    movie_title = urllib.parse.quote(movie_title)
    found_torrents = []
    
    print("Searching for movie: " + movie_title + " with quality: 4K", flush=True)
    qhd_torrents = get_torrents_list(movie_title, QUALITY_4K)
    print("Found torrents: " + str(len(qhd_torrents)) + " for movie: " + movie_title + " with quality: 4K", flush=True)
    found_torrents += qhd_torrents
    
    # print("Searching for movie: " + movie_title + " with quality: 1080P", flush=True)
    # hd_torrents = get_torrents_list(movie_title, QUALITY_1080P)
    # print("Found torrents: " + str(len(hd_torrents)) + " for movie: " + movie_title + " with quality: 1080P", flush=True)
    # found_torrents += hd_torrents
    
    print("Found a total of " + str(len(found_torrents)) + " torrents for movie: " + movie_title, flush=True)
    # Sort the torrents by seeder count
    found_torrents = sorted(found_torrents, key=lambda x: int(x["seeder_count"]), reverse=True)
    
    # Now we should resume all the torrents we paused
    # for torrent in paused_torrents:
    #     client.torrents_resume(torrent)
    
    return found_torrents
    

def get_torrents_list(movie_title, quality):
    dest_url = f'https://thepiratebay.org/search.php?q={movie_title}&all=on&search=Pirate+Search&page=0&orderby=&cat=0'
    # Attempt to load the page and gather data on torrents
    try:
        driver.get(dest_url)
    except Exception as ex:
        print("Failed to check pirate bay for movie: " + movie_title + " with quality: " + quality)
        print(ex)
        return []
    # Searching page worked, now we need to get the results
    results = driver.find_elements(By.CLASS_NAME, 'list-entry')
    if len(results) == 0:
        print("No results found for: " + movie_title + " with quality: " + quality)
        return []
    results = results[0:5]
    # If we find any, we want to print the href of the child <a> tag of the child <span> with class name "list-item" "item-name" and "item-title" of each result
    choices = []
    for result in results:
        # We want to print the text of the result element as well
        item_name = result.find_element(
            By.CLASS_NAME, 'list-item.item-name.item-title')
        # Magnet link will be the first <a> tag within this list-entry child element span with the class name "item-icons"
        magnet_link = result.find_element(
            By.CLASS_NAME, 'item-icons').find_element(By.TAG_NAME, 'a').get_attribute('href')
        item = item_name.find_element(By.TAG_NAME, 'a')
        name = item.text
        link = item.get_attribute('href')
        # Seeder count will be a number located in the child element of list-entry with the class names "list-item" and "item-seed"
        seeder_count = result.find_element(
            By.CLASS_NAME, 'list-item.item-seed').text
        # If name is "No results returned" then we skip this result
        if name != "No results returned":
            choices.append({"name": name, "link": link,
                        "magnet": magnet_link, "seeder_count": seeder_count})
    return choices
    
def resume_torrent(torrent_hash, client):
    print("Attempting to resume torrent: " + torrent_hash, flush=True)
    client.torrents_top_priority(torrent_hash)
    

def download_movie(magnet_link, client):
    dl_path = '/mnt/coldstorage/permafrost/Movies/'
    client.torrents_add(urls=magnet_link, save_path=dl_path)
