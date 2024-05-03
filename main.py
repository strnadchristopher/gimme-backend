from typing import Union
import torrentEngine
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from qbittorrentapi import Client
client = Client(
    host="http://192.168.1.144:8080",
    username="admin",
    password="adminadmin"
)
app = FastAPI()
class DownloadRequest(BaseModel):
    magnet: str
origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
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

@app.get("/search/{movie_name}")
def request_search(movie_name: str):
    return torrentEngine.search_for_movie(movie_name, client)

@app.post("/download/")
def request_download(magnet_link: DownloadRequest):
    print(magnet_link.magnet)
    # print("Downloading movie with magnet link: " + magnet_link)
    return torrentEngine.download_movie(magnet_link.magnet, client)

class ResumeRequest(BaseModel):
    torrent_hash: str
@app.post("/resume")
def resume_torrent(resume_request: ResumeRequest):
    torrentEngine.resume_torrent(resume_request.torrent_hash, client)
    return {"status": "success"}
    