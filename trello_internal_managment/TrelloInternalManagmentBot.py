import json
import os
import time

import requests


class TrelloInternalManagmentBot:
    key = {}

    def __init__(self):
        self.read_key()
        try:
            print(self.key['principal_board'])
            print(self.key['secondary_board'])
        except KeyError:
            self.get_all_board()

    def keep_alive(self):
        while True:
            self.controll_change()
            time.sleep(5)

    def read_key(self):
        with open(os.path.join(os.path.dirname(__file__), ".env"),'r') as json_file:
            self.key = json.load(json_file)

    def write_key(self):
        with open(os.path.join(os.path.dirname(__file__), ".env"),'w') as json_file:
            json.dump(self.key,json_file,indent=4)


    def controll_change(self):
        print("I AM ALIVE!!!")

    def get_all_board(self):
        url = f"https://api.trello.com/1/members/{self.key['admin_id']}/boards"

        headers = {
            "Accept": "application/json"
        }

        query = {
            'key': self.key['api_key'],
            'token': self.key['admin_token']
        }

        response = requests.request(
            "GET",
            url,
            headers=headers,
            params=query
        )
        print(response)
        self.key['secondary_board'] = {}
        self.key['principal_board'] = {}
        board_list_raw = response.json()
        for board in board_list_raw:
            print(f"{board['id'].__str__()}\t{board['name'].__str__()}")
            if board['name'] == 'UFFICIO' or board['name'] == 'FALEGNAMERIA':
                self.key['principal_board'][board['name']] = board['id']
            else:
                self.key['secondary_board'][board['name']] = board['id']


        self.write_key()

    def get_all_list(self, board_id, board_name):
        url = f"https://api.trello.com/1/boards/{board_id}/lists"

        query = {
            'key': self.key['api_key'],
            'token': self.key['admin_token']
        }

        response = requests.request(
            "GET",
            url,
            params=query
        )
        list_list = {}
        for list in response.json():
            list_list[list['name']] = list['id']

        key



    def get_all_card(self):
        pass


    def get_member_from_card(self):
        url = "https://api.trello.com/1/cards/{id}/members"

        query = {
            'key': self.key['api_key'],
            'token': self.key['admin_token']
        }

        response = requests.request(
            "GET",
            url,
            params=query
        )

        print(response)