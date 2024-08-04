import requests

def test_sse(url):
    response = requests.get(url, stream=True)
    for line in response.iter_lines():
        if line:
            print(line.decode('utf-8'))

if __name__ == "__main__":
    sse_url = "http://localhost:8000/api/search/movies/avengers"
    test_sse(sse_url)
