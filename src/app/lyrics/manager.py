import requests
import json
import xmltodict

from .baseapi import BaseAPI


class LyricsAPIManager:

    def __init__(self):
        self.apis = []

    @staticmethod
    def response_to_json(response: requests.Response):
        print("Response [Code %d]:" % response.status_code)
        print(response.raw.info())
        print(response.content)
        if response.status_code != 200:
            print("Error!")
            return False
        return json.loads(json.dumps(xmltodict.parse(response.content)))

    def add(self, api: BaseAPI):
        self.apis.append(api)

    def search(self, search: str):
        pass
