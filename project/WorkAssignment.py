import json
import os
import signal
import sys
import time
import requests
import dateutil.parser
import re
condition = True


class WorkAssigment:
    checklist = {}
    condition = True

    def __init__(self):

        signal.signal(signal.SIGINT, self.signal_handler)
        i = 0
        while self.condition:
            print("===================================================================================================")
            print(f"\t\t\t\tINIZIO CICLIO : {i}")
            print("---------------------------------------------------------------------------------------------------")
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
            self.check_clone_card_status()

            self.write_checklist()
            self.write_key()
            #time.sleep(5)
            print("---------------------------------------------------------------------------------------------------")
            print(f"\t\t\t\tFINE CICLIO ")
            print("===================================================================================================")
            i += 1



    def signal_handler(self,sig, frame):
        print('[CLOSING THE BOT]')
        self.condition = False



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
        print("[START] getting checklist")
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
                            self.checklist[trello_checklist['id']] = {"title" : trello_checklist['name'],'idCard':trello_checklist['idCard'], 'urlCard':self.get_card_link(trello_checklist['idCard']), "element":list}
                            #e in fine la salva

                    else: # se è gia stata salvata

                        for linea in trello_checklist['checkItems']:
                            if linea['id'] in self.checklist[trello_checklist['id']]['element'].keys():

                                if (linea['idMember'] != self.checklist[trello_checklist['id']]['element'][linea['id']]['member'] or linea['due'] != self.checklist[trello_checklist['id']]['element'][linea['id']]['due'])\
                                        and linea["state"] == "incomplete" :
                                    print(f"{linea['name']}:  "
                                        f"{linea['idMember']}\t {self.checklist[trello_checklist['id']]['element'][linea['id']]['member']} "
                                        f"\t {linea['idMember'] != self.checklist[trello_checklist['id']]['element'][linea['id']]['member']}\t"
                                          f"{self.checklist[trello_checklist['id']]['element'][linea['id']]['used']}")
                                    self.checklist[trello_checklist['id']]['element'][linea['id']]['member'] = linea['idMember']
                                    self.checklist[trello_checklist['id']]['element'][linea['id']]['due'] = linea['due']
                                    if self.checklist[trello_checklist['id']]['element'][linea['id']]['used'] == True:  # se non è ancora stato utilizzato
                                        url = f"https://api.trello.com/1/cards/{self.checklist[trello_checklist['id']]['element'][linea['id']]['clone_id']}"

                                        headers = {
                                            "Accept": "application/json"
                                        }

                                        query = {
                                            'key': self.key['api_key'],
                                            'token': self.key['admin_token'],
                                            'closed': "true"
                                        }

                                        response = requests.request(
                                            "PUT",
                                            url,
                                            headers=headers,
                                            params=query
                                        )
                                        print(response)
                                        self.checklist[trello_checklist['id']]['element'][linea['id']]['used'] = False
                            else:
                                print(f"[NEW LINE]{linea['id']} {linea['name']}")
                                self.checklist[trello_checklist['id']]['element'][linea['id']] = {'name':linea['name'],'due':linea['due'],'member':linea['idMember'],'used':False}
                                self.checklist[trello_checklist['id']]['element'][linea['id']]['used'] = False
        print("[END] getting checklist")
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
            #if self.key['id_board'][member] == "5ee869db1e066a18aec6ba98": #controllo
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
        print("[START] creating card")
        for key in self.checklist.keys():
            for element in self.checklist[key]['element'].keys():
                try:
                    if self.checklist[key]['element'][element]['member'] != None:
                        if self.checklist[key]['element'][element]['used'] == False:
                            # if self.checklist[key]['element'][element]['member'] == "5ed8067e73403d50623f87fd": #controllo
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
                                if response.__str__() == "<Response [200]>":
                                    self.checklist[key]['element'][element]['clone_id'] = response.json()['id']

                                    url = f"https://api.trello.com/1/cards/{response.json()['id']}/attachments"

                                    headers = {
                                        "Accept": "application/json"
                                    }

                                    query = {
                                        'key': self.key['api_key'],
                                        'token': self.key['admin_token'],
                                        'url' : self.checklist[key]['urlCard']
                                    }

                                    response = requests.request(
                                        "POST",
                                        url,
                                        headers=headers,
                                        params=query
                                    )
                                    print(response)

                except TypeError:
                    print("non va bene")
                    print(self.checklist[key]['element'])
        print("[END] creating card")
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
        print("[START] Sorting")
        mesi = {"Gennaio": 1, "Febbraio": 2, "Marzo": 3, "Aprile": 4, "Maggio": 5, "Giugno": 6, "Luglio": 7, "Agosti": 8, "Settembre": 9,
                "Ottobre": 10, "Novembre": 11, "Dicembre": 12}


        for key in self.key['id_list'].keys(): # prende tutte le liste MANAGMENT
            url = f"https://api.trello.com/1/lists/{self.key['id_list'][key]}/cards"

            query = {
                'key': self.key['api_key'],
                'token': self.key['admin_token']
            }

            response = requests.request( # chiede tutte le card nella lista
                "GET",
                url,
                params=query
            )

            if response.__str__() == "<Response [200]>": #prende i titoli e gli id delle card
                title_list = []
                title_dict = {}
                #elabora i titoli delle card in modo che possano essere ordinati
                for card in response.json():
                    title = re.sub("[^\w]", " ", card['name']).split()
                    title.append(card['id'])
                    try:
                        title[1] = mesi[title[1]]
                        title[0], title[1] = title[1], title[0]
                        title = [word.__str__() for word in title]
                        title = ' '.join(title)


                    except IndexError:
                        title = ' '.join(title)

                    except KeyError:
                        title = ' '.join(title)

                    title_dict[title] = card['id']
                    title_list.append(title)

                title_list = sorted(title_list) #ordina le card

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

        print("[END] Sorting")

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
        else:
            return response

    def check_clone_card_status(self):
        for checklist in self.checklist.keys():
            for element in self.checklist[checklist]['element'].keys():
                if self.checklist[checklist]['element'][element]['used'] == True:
                    if self.checklist[checklist]['element'][element]['clone_id'] != None:
                        if self.chek_card_status(self.checklist[checklist]['element'][element]['clone_id']):
                            url = f"https://api.trello.com/1/cards/{self.checklist[checklist]['idCard']}/checklist/{checklist}/checkItem/{element}"

                            headers = {
                                "Accept": "application/json"
                            }

                            query = {
                                'key': self.key['api_key'],
                                'token': self.key['admin_token'],
                                "state": "complete"
                            }

                            response = requests.request(
                                "PUT",
                                url,
                                headers=headers,
                                params=query
                            )

                            print(f"check_clone_card_status:\t {response}")
                            self.checklist[checklist]['element'][element]['clone_id'] = None