import requests


def find(url: str) -> list[dict]:
    return requests.get(url).json()['data']