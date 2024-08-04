from typing import Union
import torrentEngine
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from qbittorrentapi import Client
from fastapi.staticfiles import StaticFiles
from torrent_plugins import thepiratebay, one337x, bitsearch, animetosho, solidtorrents, torrentgalaxy
import json
import time
import asyncio
proxy_server_address = '192.168.1.144:48781'

client = Client(
    host="http://192.168.1.144:8080",
    username="admin",
    password="adminadmin"
)
app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:5173",
    "http://192.168.1.217:5173",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Endpoint to get current torrent queue
@app.get("/api/torrents")
def get_torrents():
    return torrentEngine.get_torrents_info(client)


def event_generator(movie_name, media_type):
    magnets_to_yield = 20
    
    plugins = [thepiratebay.thepiratebay(), 
               one337x.one337x(), 
               animetosho.animetosho(), 
               bitsearch.bitsearch(),
               solidtorrents.solidtorrents(),
               torrentgalaxy.torrentgalaxy()]
    torrents_found = 0
    for plugin in plugins:
        print(f"Searching {plugin.name} for {movie_name}")
        # When we first using a plugin, we yield an object that looks like {event: "plugin_switch", "data": plugin_name}
        yield f"data: {json.dumps({'event': 'plugin_switch', 'data': plugin.name})}\n\n"
        try:
            for torrent in plugin.search_and_yield(movie_name, media_type, proxy_server_address, magnets_to_yield):
                yield f"data: {json.dumps(torrent)}\n\n"
                torrents_found += 1
        except Exception as e:
            print(f"Error in {plugin.name}: {e}")
            # yield f"data: {json.dumps({'event': 'plugin_error', 'data': plugin.name})}\n\n"
        
    # Yield another event object, with the event being "search_completed" and the data being the number of torrents found
    yield f"data: {json.dumps({'event': 'search_completed', 'data': torrents_found})}\n\n"   
    print("Search completed, found " + str(torrents_found) + " torrents")
            

@app.get("/api/search/{media_type}/{movie_name}")
async def stream_search_results(media_type: str, movie_name: str):
    import urllib.parse
    # Clean and URL-encode the movie title
    movie_name = movie_name.replace("'", "").replace('"', "").replace("*", "")
    movie_name = urllib.parse.quote(movie_name)


    return StreamingResponse(event_generator(movie_name, media_type), media_type="text/event-stream")


class DownloadRequest(BaseModel):
    magnet: str
    media_type: str
    movie_name: str


@app.post("/api/download")
@app.post("/api/download/")
def request_download(download_request: DownloadRequest):
    print(download_request)
    # print("Downloading movie with magnet link: " + magnet_link)
    return torrentEngine.download_movie(download_request, client)


class ResumeRequest(BaseModel):
    torrent_hash: str


@app.post("/api/resume")
def resume_torrent(resume_request: ResumeRequest):
    torrentEngine.resume_torrent(resume_request.torrent_hash, client)
    return {"status": "success"}

# We're going to add functionality to add a movie to the owned list
# This is used so we know which movies we have already downloaded
# We manage this with a json file which just contains an array of movie ids, if a movie id is in this array, we consider it downloaded
# movie_id will be a number


class AddToOwnedListRequest(BaseModel):
    movie_id: int


@app.post("/api/add_to_owned_list")
def add_to_owned_list(add_to_owned_list_request: AddToOwnedListRequest):
    new_list = torrentEngine.add_to_owned_list(
        add_to_owned_list_request.movie_id)
    return new_list


class RemoveFromOwnedListRequest(BaseModel):
    movie_id: int


@app.post("/api/remove_from_owned_list")
def remove_from_owned_list(remove_from_owned_list_request: RemoveFromOwnedListRequest):
    new_list = torrentEngine.remove_from_owned_list(
        remove_from_owned_list_request.movie_id)
    return new_list

# The correct method is to have a single endpoint for toggling weather a movie is owned or not


class UpdateOwnedListRequest(BaseModel):
    movie_id: int


@app.post("/api/update_owned_list")
def update_owned_list(update_owned_list_request: UpdateOwnedListRequest):
    new_list = torrentEngine.update_owned_list(
        update_owned_list_request.movie_id)
    return new_list


@app.get("/api/owned_list")
def get_owned_list():
    return torrentEngine.get_owned_list()


class UpdatePreviousMagnetListRequest(BaseModel):
    magnet: str


@app.post("/api/update_previous_magnet_list")
def update_previous_magnet_list(update_previous_magnet_list_request: UpdatePreviousMagnetListRequest):
    new_list = torrentEngine.update_previous_magnet_list(
        update_previous_magnet_list_request.magnet)
    return new_list


@app.get("/api/previous_magnet_list")
def get_previous_magnet_list():
    return torrentEngine.get_previous_magnet_list()

