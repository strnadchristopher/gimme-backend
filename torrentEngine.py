import asyncio
import json
import time
from qbittorrentapi import Client, TorrentState
from fastapi.responses import StreamingResponse



from torrent_plugins import thepiratebay

async def search_for_movie(movie_title):
    pass
    
    
def download_movie(download_request, client):
    # Download Request will contain a magnet link, a media type, and a movie name
    # If the media_type is "movie" then we will download the movie to the Movies folder
    # If the media_type is "tv" then we will download the show to the Tv folder
    print("Downloading movie: " + download_request.movie_name, flush=True)
    print(download_request, flush=True)
    dl_path_base = '/mnt/FrostStorageShare/Media/'
    dl_path = ""
    if download_request.media_type == "movie" or download_request.media_type == "movies":
        dl_path = dl_path_base + "Movies"
    elif download_request.media_type == "tv":
        dl_path = dl_path_base + "TV"
    else:
        dl_path = dl_path_base + "Other"
    # Then add the movie name to the path at the end
    dl_path += "/" + download_request.movie_name
    client.torrents_add(urls=download_request.magnet, save_path=dl_path)

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
    # print("==========================", flush=True)
    # for torrent in currently_downloading:
    #     print("Currently downloading: " + torrent["name"] +
    #           " ETA: " + str(time.strftime('%H:%M:%S', time.gmtime(torrent["eta"]))), flush=True)
    # print("==========================", flush=True)
    # for torrent in queued_to_download:
    #     print("Queued to download: " + torrent["name"], flush=True)
    # print("\n\n", flush=True)
    return {"currently_downloading": currently_downloading, "queued_to_download": queued_to_download}

def resume_torrent(torrent_hash, client):
    print("Attempting to resume torrent: " + torrent_hash, flush=True)
    client.torrents_top_priority(torrent_hash)

# These functions open the owned_movies.json file and add or remove a movie id from the list, and then overwrite the file with the new list, and then return the list
def add_to_owned_list(movie_id):
    with open("owned_movies.json", "r") as file:
        owned_movies = json.load(file)
    # Close the file
    file.close()
    owned_movies.append(movie_id)
    with open("owned_movies.json", "w") as file:
        json.dump(owned_movies, file)
    # Close the file
    file.close()
    return owned_movies

def remove_from_owned_list(movie_id):
    with open("owned_movies.json", "r") as file:
        owned_movies = json.load(file)
    # Close the file
    file.close()
    owned_movies.remove(movie_id)
    with open("owned_movies.json", "w") as file:
        json.dump(owned_movies, file)
    # Close the file
    file.close()
    return owned_movies

def update_owned_list(movie_id):
    with open("owned_movies.json", "r") as file:
        owned_movies = json.load(file)
    # Close the file
    file.close()
    if movie_id in owned_movies:
        owned_movies.remove(movie_id)
    else:
        owned_movies.append(movie_id)
    with open("owned_movies.json", "w") as file:
        json.dump(owned_movies, file)
    # Close the file
    file.close()
    return owned_movies

def get_owned_list():
    import json
    with open("owned_movies.json", "r") as file:
        owned_movies = json.load(file)
    # Close the file
    file.close()
    return owned_movies

def update_previous_magnet_list(magnet):
    with open("previous_magnet_list.json", "r") as file:
        previous_magnet_list = json.load(file)
    # Close the file
    file.close()
    previous_magnet_list.append(magnet)
    with open("previous_magnet_list.json", "w") as file:
        json.dump(previous_magnet_list, file)
    # Close the file
    file.close()
    return previous_magnet_list

def get_previous_magnet_list():
    with open("previous_magnet_list.json", "r") as file:
        previous_magnet_list = json.load(file)
    # Close the file
    file.close()
    return previous_magnet_list