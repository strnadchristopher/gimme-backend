import torrentEngine

def start():
    # First, we need to determine if we are running in cli chat mode, or if we are starting in server mode so we can use endpoints to interact with this program
    # If there's command line arguments, every command line argument is part of one phrase which is the movie search term, and we'll join them all together, and search for that movie
    import sys
    if len(sys.argv) > 1:
        # We need to check if the flag -s is present, if so, it means we're starting in server mode
        if "-s" in sys.argv:
            server_mode()
        else:
            # If that flag is not present, then we will presume are in cli mode, and we will search for the movie name
            movie_name = ' '.join(sys.argv[1:])
            cli_mode(movie_name)
    else:
        cli_mode()


def server_mode():
    import subprocess
    print("Starting in server mode...", flush=True)
    ssl_command = [
        "uvicorn",
        "main:app",  # Assuming your FastAPI instance is in main.py and called app
        "--reload",  # Auto-reload when code changes
        "--host", "0.0.0.0",
        "--port", "6970",
        "--ssl-keyfile", "keys/key.pem",
        "--ssl-certfile", "keys/cert.pem"
    ]
    command = [
        "uvicorn",
        "main:app",  # Assuming your FastAPI instance is in main.py and called app
        "--reload",  # Auto-reload when code changes
        "--host", "0.0.0.0",
        "--port", "6970",
    ]
    subprocess.run(command)
    # subprocess.run("uvicorn main:app --reload --host 0.0.0.0 --port 6970 --ssl-keyfile keys/key.pem --", shell = True)


def cli_mode(search_query=None):
    # Create QBitTorrentClient
    from qbittorrentapi import Client
    client = Client(
        host="http://192.168.1.217:8080",
        username="admin",
        password="adminadmin"
    )
    
    torrentEngine.get_torrents_info(client)
    found_torrents = []
    if search_query is not None:
        print("'Searching for movie: " + search_query + "'...", flush=True)
        found_torrents = torrentEngine.search_for_movie(search_query, client=client)
    else:
        print_greeting()
        movie_name = input()
        found_torrents = torrentEngine.search_for_movie(movie_name, client=client)
    choice_num = 1
    for choice in found_torrents:
        print("[" + str(choice_num) + "] " + choice["name"] +
            " [" + choice["seeder_count"] + " seeders]")
        choice_num += 1
    choice_num = input("Choose a torrent to download, or press enter to skip: ")
    try:
        choice_num = int(choice_num)
    except:
        print("Invalid choice, nevermind...")
        exit(0)
    torrentEngine.download_movie(found_torrents[choice_num-1]["magnet"], client)
    print("Added: " + found_torrents[choice_num-1]["name"] + " to download queue with " +
          found_torrents[choice_num-1]["seeder_count"] + " seeders.", flush=True)
    

def print_greeting():
    # Just for fun, we have a list of title we call the user, names that are exalting to the user
    # Make a very creative list, names that you would call a mythical figure or god figure or hero, make them very grandiose, and not too similar to eachother, be extremely creative
    user_titles = [
        "Exalted One",
        "All Knowing One",
        "All Intelligent One",
        "Eater of Worlds",
        "My Dear Creator",
        "My Dear Master",
        "People's Champion",
        "He Who Devours",
        "He Who Creates",
        "He Who Destroys",
        "He Who Knows All",
        "Christopher, The Infinite One",
        "Christopher, The All Knowing",
        "Christopher, The All Intelligent",
        "Bone Crusher",
        "The Great Destroyer",
        "The Great Creator",
        "My Sweet Champion",
        "He Who Contains Multitude",
        "He Who Is All",
    ]
    # If there's no command line arguments, we'll ask the user to input the movie name
    # Ask the user what movie name they want to search for
    import random
    # Pick a random title from user titles
    chosen_title = random.choice(user_titles)
    print(chosen_title + ", what movie would you like to search for?")

start()
