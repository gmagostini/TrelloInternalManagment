import json
import os
import time

import requests


class TrelloInternalManagmentBot:
    key = {}
    user = {}

    def __init__(self):
        self.read_key()
        self.read_user()
        self.query={
            'key': self.key['api_key'],
            'token': self.key['admin_token']
        }

        try:
            self.key['principal_board']
            self.key['secondary_board']
        except KeyError:
            self.get_all_board()

        if 'card_list' not in self.key.keys():
            self.key['card_list'] = {}
            print("ho create card_list")

        if 'user' not in self.key.keys():
            self.key['user'] = {}
            print("ho create user")

        for key in self.key['principal_board'].keys():
            self.get_activity(key)

        self.write_key()


    def keep_alive(self):
        while True:
            self.controll_change()

    def read_key(self):
        with open(os.path.join(os.path.dirname(__file__), ".env"), 'r') as json_file:
            self.key = json.load(json_file)

    def write_key(self):
        with open(os.path.join(os.path.dirname(__file__), ".env"), 'w') as json_file:
            json.dump(self.key,json_file,indent=4)


    def read_user(self):
        with open(os.path.join(os.path.dirname(__file__), ".utenti"), 'r') as json_file:
            self.user = json.load(json_file)


    def controll_change(self):
        print("I AM ALIVE!!!")

    def get_all_board(self):
        #time.sleep(10/300)
        url = f"https://api.trello.com/1/members/{self.key['admin_id']}/boards"

        headers = {
            "Accept": "application/json"
        }


        response = requests.request(
            "GET",
            url,
            headers=headers,
            params=self.query
        )
        self.problem(response,"get_all_board")
        print(response)
        self.key['secondary_board'] = {}
        self.key['principal_board'] = {}
        board_list_raw = response.json()
        for board in board_list_raw:
            print(f"{board['id'].__str__()}\t{board['name'].__str__()}")
            if board['name'] == 'UFFICIO' or board['name'] == 'FALEGNAMERIA':
                self.key['principal_board'][board['id']] = board['name']
            else:
                self.key['secondary_board'][board['id']] = board['name']



    def get_activity(self, boardId):
        url = f"https://api.trello.com/1/boards/{boardId}/actions"

        response = requests.request(
            "GET",
            url,
            params=self.query
        )

        lista = {}
        i=0
        print(response.json()[0])
        for activiy in response.json():
            lista[activiy['id']] = activiy['type']
            print(f"{i}\t{activiy['id']}\t{activiy['type']}\t{activiy['date']}")

        with open(os.path.join(os.path.dirname(__file__), ".action"), 'w') as json_file:
            json.dump(self.key, json_file, indent=4)





    def problem(self,responste,text):
        if responste.__str__() == "<Response [429]>":
            print(f"{text}:\t{responste.json()}")

