from typing import Union
import torrentEngine
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from qbittorrentapi import Client
from fastapi.staticfiles import StaticFiles

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
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Endpoint to get current torrent queue
@app.get("/torrents")
def get_torrents():
    return torrentEngine.get_torrents_info(client)

@app.get("/search/{movie_name}/{page}")
def request_search(movie_name: str, page: int):
    return torrentEngine.search_for_movie(movie_name, page, client)

class DownloadRequest(BaseModel):
    magnet: str
    media_type: str
    movie_name: str
    
@app.post("/download/")
def request_download(download_request: DownloadRequest):
    print(download_request)
    # print("Downloading movie with magnet link: " + magnet_link)
    return torrentEngine.download_movie(download_request, client)

class ResumeRequest(BaseModel):
    torrent_hash: str
@app.post("/resume")
def resume_torrent(resume_request: ResumeRequest):
    torrentEngine.resume_torrent(resume_request.torrent_hash, client)
    return {"status": "success"}
    
# We're going to add functionality to add a movie to the owned list
# This is used so we know which movies we have already downloaded
# We manage this with a json file which just contains an array of movie ids, if a movie id is in this array, we consider it downloaded
# movie_id will be a number
class AddToOwnedListRequest(BaseModel):
    movie_id: int
@app.post("/add_to_owned_list")
def add_to_owned_list(add_to_owned_list_request: AddToOwnedListRequest):
    new_list = torrentEngine.add_to_owned_list(add_to_owned_list_request.movie_id)
    return new_list

class RemoveFromOwnedListRequest(BaseModel):
    movie_id: int
@app.post("/remove_from_owned_list")
def remove_from_owned_list(remove_from_owned_list_request: RemoveFromOwnedListRequest):
    new_list = torrentEngine.remove_from_owned_list(remove_from_owned_list_request.movie_id)
    return new_list

# The correct method is to have a single endpoint for toggling weather a movie is owned or not
class UpdateOwnedListRequest(BaseModel):
    movie_id: int
@app.post("/update_owned_list")
def update_owned_list(update_owned_list_request: UpdateOwnedListRequest):
    new_list = torrentEngine.update_owned_list(update_owned_list_request.movie_id)
    return new_list
    
@app.get("/owned_list")
def get_owned_list():
    return torrentEngine.get_owned_list()