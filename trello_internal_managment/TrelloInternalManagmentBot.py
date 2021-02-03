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
        if 'liste' not in self.key.keys():
            self.key['liste'] = {}
            print("ho create liste")

        if 'card_list' not in self.key.keys():
            self.key['card_list'] = {}
            print("ho create card_list")


        if 'user' not in self.key.keys():
            self.key['user'] = {}
            print("ho create user")

        for key in self.key['principal_board'].keys():
            print(key)
            self.get_all_card(key, self.key['principal_board'][key])

        self.write_key()


    def keep_alive(self):
        while True:
            self.controll_change()

    def read_key(self):
        with open(os.path.join(os.path.dirname(__file__), ".env"),'r') as json_file:
            self.key = json.load(json_file)

    def write_key(self):
        with open(os.path.join(os.path.dirname(__file__), ".env"),'w') as json_file:
            json.dump(self.key,json_file,indent=4)


    def read_user(self):
        with open(os.path.join(os.path.dirname(__file__), ".utenti"),'r') as json_file:
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




    def get_all_list(self, board_id, board_name):

        url = f"https://api.trello.com/1/boards/{board_id}/lists"


        response = requests.request(
            "GET",
            url,
            params=self.query
        )
        self.problem(response,"get_all_card")
        list_list = {}
        print(board_name)
        for list in response.json():
            list_list[list['id']] = list['name']
            print(f"{list['id']}\t{list['name']}")

        self.key['liste'][board_name] = list_list





    def get_all_card(self, lists_id, list_name):

        url = f"https://api.trello.com/1/boards/{lists_id}/cards"


        response = requests.request(
            "GET",
            url,
            params=self.query
        )
        self.problem(response,"get_all_card")
        print(list_name)
        print(response)
        for card in response.json():

            print(f"{card['id']}\t{card['name']}\t{self.get_username_from_id(card['idMembers'])}")

            self.key['card_list'][card['id']] = card['name'],self.get_username_from_id(card['idMembers'])


    def get_username_from_id(self, user_id_list):
        risposta = []

        for user_id in user_id_list:
            if user_id not in self.key['user'].keys():
                url = f"https://api.trello.com/1/members/{user_id}"

                headers = {
                    "Accept": "application/json"
                }


                response = requests.request(
                    "GET",
                    url,
                    headers=headers,
                    params=self.query
                )

                self.problem(response,"get_username_from_id")

                self.key['user'][response.json()['id']] = response.json()['username']
                risposta.append([response.json()['id'],response.json()['username'],self.user[response.json()['username']]])
            else:
                risposta.append([user_id, self.key['user'][user_id], self.user[self.key['user'][user_id]]])

        return risposta

    def problem(self,responste,text):
        if responste.__str__() == "<Response [429]>":
            print(f"{text}:\t{responste.json()}")

