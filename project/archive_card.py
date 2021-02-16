import os

import requests
import json



with open(os.path.join(os.path.dirname(__file__), "data", ".env"), 'r') as json_file:
    key = json.load(json_file)


    url = "https://api.trello.com/1/cards/602ba6bd354b0778f3156699"

    headers = {
       "Accept": "application/json"
    }

    query = {
        'key': key['api_key'],
        'token': key['admin_token'],
        'closed': "true"
    }

    response = requests.request(
       "PUT",
       url,
       headers=headers,
       params=query
    )
    print(response)
    if response.__str__() == "<Response [200]>":
        print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))


