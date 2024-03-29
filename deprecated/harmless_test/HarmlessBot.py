import json
import os
import time
import requests



class TrelloInternalManagmentBot:
    key = {}
    user = {}
    card_list = []

    def __init__(self):

        while True:
            print("=======================================================================")
            print("\t\t\tINIZIO CICLO")
            print("=======================================================================")
            try:
                self.read_key()
                self.read_user()
                self.read_cards()
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

                if 'list' not in self.key.keys():
                    self.key['list'] = {}
                    print("ho create card_list")


                if 'user' not in self.key.keys():
                    self.key['user'] = {}
                    print("ho create user")

                for key in self.key['principal_board'].keys():
                    self.get_all_card(key, self.key['principal_board'][key])

                self.check_managment_list()
                self.create_card_link()
                #self.check_link_persistence()
            except KeyError as e:
                print(f"[warning] Kyeerror: {e.__str__()}")
                self.write_key()
                self.write_cards()


            print("=======================================================================")
            print("\t\t\tFINE CICLO")
            print("=======================================================================")
            time.sleep(10)



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


    def read_cards(self):
        with open(os.path.join(os.path.dirname(__file__), ".cards"), 'r') as json_file:
            self.card_list = json.load(json_file)

    def write_cards(self):
        with open(os.path.join(os.path.dirname(__file__), ".cards"), 'w') as json_file:
            json.dump(self.card_list,json_file,indent=4)


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

        print(f"get_all_board{response}")
        self.key['secondary_board'] = {}
        self.key['principal_board'] = {}
        board_list_raw = response.json()
        for board in board_list_raw:
            print(f"{board['id'].__str__()}\t{board['name'].__str__()}")
            if board['name'] == 'cavallo' or board['name'] == 'FALEGNAMERIA':
                self.key['principal_board'][board['id']] = board['name']
            else:
                self.key['secondary_board'][board['id']] = board['name']






    def get_all_card(self, lists_id, list_name):
        url = f"https://api.trello.com/1/boards/{lists_id}/cards"


        response = requests.request(
            "GET",
            url,
            params=self.query
        )

        print(list_name)
        print(f"get_all_card{response}")
        id_cards_saved = self.card_list.keys()

        for card in response.json():
            if card['id'] not in id_cards_saved:
                print(f"[SAVED]{card['id']}\t{card['name']}\t{card['shortUrl']}\t{self.get_username_from_id(card['idMembers'])}")
                self.get_card_action(card['id'])
                self.card_list[card['id']] = {"name": card['name'], "member" : self.get_username_from_id(card['idMembers']),
                                              "link":card['shortUrl'],"desc":card['desc'],'dateLastActivity':card['dateLastActivity'],
                                              "linked":[]}
            else:
                for key in self.card_list.keys():
                    if card['id'] == key:
                        if card['dateLastActivity'] != self.card_list[key]['dateLastActivity']:
                            self.card_list[card['id']] = {"name": card['name'],
                                                          "member": self.get_username_from_id(card['idMembers']),
                                                          "link": card['shortUrl'], "desc": card['desc'],
                                                          'dateLastActivity': card['dateLastActivity'], "linked": []}

                            print(f"[UPDATE]{card['id']}\t{card['name']}\t\t{self.get_username_from_id(card['idMembers'])}")
                            print(f"cambio membri {card['idMembers']} \t {self.card_list[key]['member']}")


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



                self.key['user'][response.json()['id']] = response.json()['username']
                self.key['user'][response.json()['username']] = response.json()['id']
                risposta.append([response.json()['id'],response.json()['username'],self.user[response.json()['username']]])
            else:
                risposta.append([user_id, self.key['user'][user_id], self.user[self.key['user'][user_id]]])

        return risposta

    def get_card_action(self,card_id):
        url = f"https://api.trello.com/1/cards/{card_id}/actions"

        headers = {
            "Accept": "application/json"
        }
        response = requests.request(
            "GET",
            url,
            headers=headers,
            params=self.query
        )

        for action in response.json():
            pass
            #print(f"action {action['id']}\t{action['type']}\t{action['date']}")


    def check_managment_list(self):

        #print(self.key['user']['marcozaninelli'])
        for meber in self.key['board_user'].keys():
            url = f"https://api.trello.com/1/boards/{self.key['board_user'][meber]}/lists"
            #print(f"member: {meber}")
            response = requests.request(
                "GET",
                url,
                params=self.query
            )
            #print(f"check_managment_list{response}")
            list_list = []
            list_id = {}
            if response.__str__() == "<Response [200]>":
                for list in response.json():
                    list_list.append(list['name'])
                    list_id[list['name']] = list['id']

                if "MANAGMEENT" not in list_list:
                    url = "https://api.trello.com/1/lists"

                    query_b = {
                        'key': self.key['api_key'],
                        'token': self.key['admin_token'],
                        'name' : 'MANAGMEENT',
                        'idBoard': self.key['user']["marcozaninelli"]
                    }

                    response = requests.request(
                        "POST",
                        url,
                        params=query_b
                    )


                    if response.__str__() == "<Response [200]>":
                        #print(f"ho creatmo managment {response.text}")
                        self.key['list'][meber] = response.json()['id']
                    else:
                        print(f"check_managment_list c'è un problema {response.text}")

                else:
                    #print(f"Managment list {meber} esiste già {response}")
                    self.key['list'][meber] = list_id["MANAGMEENT"]



    def create_card_link(self):
        for key in self.card_list.keys():
            if not self.card_list[key]['linked']:
                for member in self.card_list[key]["member"]:
                    url = "https://api.trello.com/1/cards"

                    query_a = self.query
                    query_a['idList']=  self.key["list"][member[1]]
                    query_a['name'] = self.card_list[key]['name']
                    query_a['desc'] = self.card_list[key]['desc']
                    response = requests.request(
                        "POST",
                        url,
                        params=query_a
                    )
                    self.card_list[key]['linked'].append(response.json()['id'])
                    if response.__str__() == "<Response [200]>":
                        print(f"[creata card] {response.json()['id']}\t{response.json()['name']}\t[{member[1]}]")
                        url = f"https://api.trello.com/1/cards/{response.json()['id']}/attachments"

                        headers = {
                            "Accept": "application/json"
                        }
                        query_b = self.query
                        query_b['url'] = self.card_list[key]['link']
                        response = requests.request(
                            "POST",
                            url,
                            headers=headers,
                            params=query_b
                        )
                        print(f"[ADD ATATCHMENT]: {response}")


                    else:
                        print(f"[card ERRORE] {response.text}")


    def check_link_persistence(self,):
        print("check_link_persistence")
        id_list = []
        for list in self.key['list'].keys():
            url = f"https://api.trello.com/1/lists/{self.key['list'][list]}/cards"

            response = requests.request(
                "GET",
                url,
                params=self.query
            )

            if response.__str__() == "<Response [200]>":
                for card in response.json():
                    id_list.append(card['id'])

            for card in self.card_list:
                for link in card['linked']:
                    if link in id_list:
                       print(f"Esiste ancora: {link}")
                    else:
                        print(f"non esiste più: {link}")
                        card['linked'].remove(link)




