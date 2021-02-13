# This code sample uses the 'requests' library:
# http://docs.python-requests.org
import requests
import json
import os


with open(os.path.join(os.path.dirname(__file__), ".env"), 'r') as json_file:
    key = json.load(json_file)
    for username in key['board_user'].keys():

        url = f"https://api.trello.com/1/members/{username}"

        headers = {
           "Accept": "application/json"
        }

        query = {
           'key': '0471642aefef5fa1fa76530ce1ba4c85',
           'token': '9eb76d9a9d02b8dd40c2f3e5df18556c831d4d1fadbe2c45f8310e6c93b5c548'
        }

        response = requests.request(
           "GET",
           url,
           headers=headers,
           params=query
        )

        print(response)
        if response.__str__() == "<Response [200]>":
            print(response.json()['id'])