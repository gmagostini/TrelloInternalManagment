# This code sample uses the 'requests' library:
# http://docs.python-requests.org
import requests
import json
import os


with open(os.path.join(os.path.dirname(__file__), "data/.env"), 'r') as json_file:
    key = json.load(json_file)
    for username in key['usernam_board'].keys():

        url = f"https://api.trello.com/1/members/{username}"

        headers = {
           "Accept": "application/json"
        }

        query = {
            'key': key['api_key'],
            'token': key['admin_token']
        }

        response = requests.request(
           "GET",
           url,
           headers=headers,
           params=query
        )

        print(response)
        if response.__str__() == "<Response [200]>":
            print(response.json()['id'] + "\t" + response.json()['username'])