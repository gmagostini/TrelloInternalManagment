import json
import os
import time
import requests
import dateutil.parser
import re

class WorkAssigment:
    checklist = {}
    def __init__(self):
        i = 0
        while True:
            print("===================================================================================================")
            print(f"\t\t\t\tINIZIO CICLIO : {i}")
            print("===================================================================================================")
            self.read_key()
            self.read_checklist()
            self.query = {
                'key': self.key['api_key'],
                'token': self.key['admin_token']
            }

            self.gett_all_checklist()
            self.check_managment()
            self.create_card()
            self.order_list()


            self.write_checklist()
            self.write_key()
            time.sleep(10)
            print("===================================================================================================")
            print(f"\t\t\t\tFINE CICLIO : {i}")
            print("===================================================================================================")
            i += 1

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
                for trello_checklist in response.json():

                    if trello_checklist['id'] not in self.checklist.keys(): #Controlla se la cheklist sia gia stata salvata

                        if self.chek_card_status(trello_checklist['idCard']) == False: # Se no controlla che non sia in una card chiuse
                            list = {}
                            print(f"[NEW]{trello_checklist['id']}\t{trello_checklist['name']}")
                            for linea in trello_checklist['checkItems']:
                                list[linea['id']] = {'name':linea['name'],'due':linea['due'],'member':linea['idMember'],'used':False}
                                print(f"\t\t{linea['id']}\t{linea['name']}")
                            self.checklist[trello_checklist['id']] = {"title" : trello_checklist['name'], 'urlCard':self.get_card_link(trello_checklist['idCard']), "element":list}
                            #e in fine la salva

                    else: # se è gia stata salvata

                        for linea in trello_checklist['checkItems']:
                            if linea['id'] in self.checklist[trello_checklist['id']]['element'].keys():
                                if linea['idMember'] != self.checklist[trello_checklist['id']]['element'][linea['id']]['member']:
                                    self.checklist[trello_checklist['id']]['element'][linea['id']]['used'] = False
                            else:
                                print(f"[NEW LINE]{linea['id']} {linea['name']}")
                                self.checklist[trello_checklist['id']]['element'][linea['id']] = {'name':linea['name'],'due':linea['due'],'member':linea['idMember'],'used':False}
                                self.checklist[trello_checklist['id']]['element'][linea['id']]['used'] = False

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

                response = requests.request(
                    "GET",
                    url,
                    params=self.query
                )


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

                            self.key['id_list'][member] = response.json()['id']
                        else:
                            print(f"check_managment_list c'è un problema {response.text}")
                    else:
                        self.key['id_list'][member] = list_name[0]



    def create_card(self):

        for key in self.checklist.keys():
            for element in self.checklist[key]['element'].keys():
                try:
                    if self.checklist[key]['element'][element]['member'] != None:
                        if self.checklist[key]['element'][element]['used'] == False:
                            if self.checklist[key]['element'][element]['member'] == "5ed8067e73403d50623f87fd":
                                url = f"https://api.trello.com/1/cards"
                                query = {
                                    'key': self.key['api_key'],
                                    'token': self.key['admin_token'],
                                    'idList': self.key['id_list'][self.checklist[key]['element'][element]['member']],
                                    'name' : f"[{self.convert_date(self.checklist[key]['element'][element]['due'])}] {self.checklist[key]['element'][element]['name']}",
                                    'due' : self.checklist[key]['element'][element]['due']
                                }

                                response = requests.request(
                                    "POST",
                                    url,
                                    params=query
                                )
                                self.checklist[key]['element'][element]['used'] = True
                except TypeError:
                    print("non va bene")
                    print(self.checklist[key]['element'])

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
                title_list = []
                title_dict = {}
                for card in response.json():
                    title = re.sub("[^\w]", " ", card['name']).split()
                    title.append(card['id'])
                    try:
                        title[1] = mesi[title[1]]
                        title = [word.__str__() for word in title]
                        title = ' '.join(title)


                    except IndexError:
                        title = ' '.join(title)

                    except KeyError:
                        title = ' '.join(title)

                    title_dict[title] = card['id']
                    title_list.append(title)

                title_list = sorted(title_list)

                i = 0
                for i in range(0,len(title_list),1):
                    url = f"https://api.trello.com/1/cards/{title_dict[title_list[i]]}"

                    headers = {
                        "Accept": "application/json"
                    }

                    query = {
                        'key': self.key['api_key'],
                        'token': self.key['admin_token'],
                        'pos' : i+1
                    }

                    response = requests.request(
                        "PUT",
                        url,
                        headers=headers,
                        params=query
                    )



    def chek_card_status(self,id_card):
        url = f"https://api.trello.com/1/cards/{id_card}"

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

        if response.__str__() == "<Response [200]>":

            return response.json()['closed']
