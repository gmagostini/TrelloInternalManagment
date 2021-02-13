import json
import os
import time
import requests
import dateutil.parser
import re

class WorkAssigment:
    checklist = {}
    def __init__(self):
        self.read_key()
        self.read_checklist()
        self.query = {
            'key': self.key['api_key'],
            'token': self.key['admin_token']
        }

        self.gett_all_checklist()
        self.check_managment()
        self.create_card()
        self.write_checklist()
        self.order_list()
        self.write_key()

    def read_key(self):
        """Leggi il dizzionario [self.key]"""
        with open(os.path.join(os.path.dirname(__file__), "data", ".env"), 'r') as json_file:
            self.key = json.load(json_file)

    def write_key(self):
        """Scrivi il dizzionario [self.key]"""
        with open(os.path.join(os.path.dirname(__file__), "data", ".env"), 'w') as json_file:
            json.dump(self.key,json_file,indent=4)

    def read_user(self):
        """Leggi il dizzionario [self.user]"""
        with open(os.path.join(os.path.dirname(__file__), "data/.utenti"), 'r') as json_file:
            self.user = json.load(json_file)

    def read_checklist(self):
        """Leggi il dizzionario [self.checklist]"""
        with open(os.path.join(os.path.dirname(__file__), "data", ".checklist"), 'r') as json_file:
            self.checklist = json.load(json_file)

    def write_checklist(self):
        """Scrivi il dizzionario [self.checklist]"""
        with open(os.path.join(os.path.dirname(__file__), "data", ".checklist"), 'w') as json_file:
            json.dump(self.checklist,json_file,indent=4)

    def gett_all_checklist(self):
        """Cerca e aggiorna tuttle le checklist dalle tabelle principali e aggiorna il dizzionario self.checklist"""
        for board in self.key['principal_board'].keys():
            url = f"https://api.trello.com/1/boards/{board}/checklists"

            response = requests.request(
                "GET",
                url,
                params=self.query
            )

            if response.__str__() == "<Response [200]>":
                for elemento in response.json():
                    if elemento['id'] not in self.checklist.keys():
                        list = []
                        print(f"[NEW]{elemento['id']}\t{elemento['name']}")
                        for linea in elemento['checkItems']:
                            list.append({'id':linea['id'],'name':linea['name'],'due':linea['due'],'member':linea['idMember']})
                            print(f"\t\t{linea['id']}\t{linea['name']}")
                        self.checklist[elemento['id']] = {"title" : elemento['name'], 'urlCard':self.get_card_link(elemento['idCard']), "element":list}

    def get_card_link(self,idCard):
        """ricava il link della card attraverso il codice"""
        url = f"https://api.trello.com/1/cards/{idCard}"

        headers = {
            "Accept": "application/json"
        }

        response = requests.request(
            "GET",
            url,
            headers=headers,
            params=self.query
        )

        if response.__str__() == "<Response [200]>":
            return response.json()['shortUrl']
        else:
            return None

    def check_managment(self):
        for member in self.key['id_board'].keys():
            if self.key['id_board'][member] == "5ee869db1e066a18aec6ba98":
                url = f"https://api.trello.com/1/boards/{self.key['id_board'][member]}/lists"
                # print(f"member: {meber}")
                response = requests.request(
                    "GET",
                    url,
                    params=self.query
                )
                # print(f"check_managment_list{response}")

                if response.__str__() == "<Response [200]>":
                    list_name = [name['id'] for name in response.json() if name['name'] == "MANAGMEENT"]
                    if not list_name:
                        url = "https://api.trello.com/1/lists"
                        query = {
                            'key': self.key['api_key'],
                            'token': self.key['admin_token'],
                            'name': 'MANAGMEENT',
                            'idBoard': self.key['id_board'][member]
                        }

                        response = requests.request(
                            "POST",
                            url,
                            params=query
                        )

                        if response.__str__() == "<Response [200]>":
                            # print(f"ho creatmo managment {response.text}")
                            self.key['id_list'][member] = response.json()['id']
                        else:
                            print(f"check_managment_list c'è un problema {response.text}")
                    else:
                        print(list_name)
                        self.key['id_list'][member] = list_name[0]



    def create_card(self):
        i = 1
        for key in self.checklist.keys():
            for element in self.checklist[key]['element']:
                if element['member'] != None:
                    if element['member'] == "5ed8067e73403d50623f87fd":
                        url = f"https://api.trello.com/1/cards"
                        query = {
                            'key': self.key['api_key'],
                            'token': self.key['admin_token'],
                            'idList': self.key['id_list'][element['member']],
                            'name' : f"[{self.convert_date(element['due'])}] {element['name']}",
                            'due' : element['due'],
                        }

                        response = requests.request(
                            "POST",
                            url,
                            params=query
                        )
                        i = i+1

    def convert_date(self,date):
        mesi = ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", "Luglio", "Agosti", "Settembre",
                "Ottobre", "Novembre", "Dicembre"]
        if date != None:
            temp =dateutil.parser.parse(date).date()
            mese = mesi[int(temp.__str__()[5:7])-1]
            giorno = temp.__str__()[8:10]
            return f"{giorno} {mese}"
        else:
            return ""


    def order_list(self):
        mesi = {"Gennaio": 1, "Febbraio": 2, "Marzo": 3, "Aprile": 4, "Maggio": 5, "Giugno": 6, "Luglio": 7, "Agosti": 8, "Settembre": 9,
                "Ottobre": 10, "Novembre": 11, "Dicembre": 12}

        for key in self.key['id_list'].keys():
            url = f"https://api.trello.com/1/lists/{self.key['id_list'][key]}/cards"

            query = {
                'key': self.key['api_key'],
                'token': self.key['admin_token']
            }

            response = requests.request(
                "GET",
                url,
                params=query
            )

            if response.__str__() == "<Response [200]>":
                for card in response.json():
                    title = re.sub("[^\w]", " ", card['name']).split()
                    try:
                        title[1] = mesi[title[1]]

                        print()
                    except IndexError:
                        pass