import json
import os

import requests

with open(os.path.join(os.path.dirname(__file__), "data/.env"), 'r') as json_file:
   key = json.load(json_file)
   idCard = "602bcfced81264300f8dee74"
   idChecklist = "602bcfd7f1bda3271c8fd029"
   idCheckItem = "602bcfdbe14137489eae826f"

   url = f"https://api.trello.com/1/cards/{idCard}/checklist/{idChecklist}/checkItem/{idCheckItem}"

   headers = {
      "Accept": "application/json"
   }

   query = {
      'key': key['api_key'],
      'token': key['admin_token'],
      "state": "incomplete"
   }

   response = requests.request(
      "PUT",
      url,
      headers=headers,
      params=query
   )

   print(response)