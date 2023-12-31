import requests
import datetime
import urllib3,json
from requests.auth import HTTPBasicAuth
import csv
from openpyxl import Workbook
from openpyxl import load_workbook

import tkinter as tk
import os,time
import multiprocessing
from tkinter import ttk
from tkinter import scrolledtext

from tkinter import Menu
from tkinter import messagebox as msg
from threading import Thread




class FMC_TEST():
    def __init__(self,FMC_IP,FMC_USER,FMC_PASS):
        urllib3.disable_warnings()
        self.FMC_IP = FMC_IP
        self.FMC_USER = FMC_USER
        self.FMC_PASS = FMC_PASS

        self.AUTH_INFO = (self.FMC_USER,self.FMC_PASS)

        self.token_uri = "/api/fmc_platform/v1/auth/generatetoken"
        self.url = "https://" + self.FMC_IP + self.token_uri





        self.response = requests.post(self.url,verify=False,auth=HTTPBasicAuth(self.FMC_USER, self.FMC_PASS))

        #응답헤더에서 아래값 추출
        self.access_token = self.response.headers["X-auth-access-token"]
        self.refresh_token = self.response.headers["X-auth-refresh-token"]
        self.DOMAIN_UUID = self.response.headers["DOMAIN_UUID"]



        self.host = []

        self.HEADER_JSON = {'accept': 'application/json',
                            'Content-Type': 'application/json',
                            'x-auth-access-token': self.access_token}


        self.DEVICE_Dict = {} # Mapping Name <-> ID

        self.ACP_Dict = {} # Mapping Name <-> ID

        self.Zone_Dict = {} # Mapping Name <-> ID


        self.Source_Object_NAME = []
        self.Source_Object_ID = []
        self.Source_Object_Dict = {}



    def Get_DeviceList(self):
        host_api_uri = "https://" + self.FMC_IP + "/api/fmc_config/v1/domain/" + self.DOMAIN_UUID + "/devices/devicerecords"
        response = requests.get(host_api_uri, headers=self.HEADER_JSON,verify=False)
        temp = json.loads(response.text)

        device_id_list = [temp['items'][num]['id'] for num in range(len(temp['items']))] # Device UUID == Container UUID
        device_name_list = [temp['items'][num]['name'] for num in range(len(temp['items']))] # Device Name

        for num in range(len(temp['items'])):
            self.DEVICE_Dict[device_name_list[num]] = device_id_list[num]

        print(self.DEVICE_Dict.keys())


    def Get_ACP(self):
        host_api_uri = "https://" + self.FMC_IP + "/api/fmc_config/v1/domain/" + self.DOMAIN_UUID + "/policy/accesspolicies"
        response = requests.get(host_api_uri, headers=self.HEADER_JSON,verify=False)
        temp = json.loads(response.text)

        acp_id_list = [temp['items'][num]['id'] for num in range(len(temp['items']))] # ACP UUID == Container UUID
        acp_name_list = [temp['items'][num]['name'] for num in range(len(temp['items']))] # Device Name
        for num in range(len(temp['items'])):
            self.ACP_Dict[acp_name_list[num]] = acp_id_list[num]

    def Show_ACP(self):
        self.Get_ACP()
        print(self.ACP_Dict.keys())


    def Get_SecurityZone(self):
        host_api_uri = "https://" + self.FMC_IP + "/api/fmc_config/v1/domain/" + self.DOMAIN_UUID + "/object/securityzones"
        response = requests.get(host_api_uri, headers=self.HEADER_JSON,verify=False)
        temp = json.loads(response.text)

        zone_id_list = [temp['items'][num]['id'] for num in range(len(temp['items']))] # ACP UUID == Container UUID
        zone_name_list = [temp['items'][num]['name'] for num in range(len(temp['items']))] # Device Name

        for num in range(len(temp['items'])):
            self.Zone_Dict[zone_name_list[num]] = zone_id_list[num]

    def Show_SecurityZone(self):
        self.Get_SecurityZone()
        print(self.Zone_Dict.keys())

        print(self.Zone_Dict['INSIDE'])
        print(self.Zone_Dict['OUTSIDE'])


    def Create_ACP(self):
        acp_name = input("input ACP NAME: ")

        data = {
                  "type": "AccessPolicy",
                  "name": acp_name,
                  "defaultAction": {
                    "action": "BLOCK"
                  }
                }

        host_api_uri = "https://" + self.FMC_IP + "/api/fmc_config/v1/domain/" + self.DOMAIN_UUID + "/policy/accesspolicies"
        response = requests.post(host_api_uri, headers=self.HEADER_JSON,data=json.dumps(data),verify=False)
        if response.status_code == 201 : print('{} is created successfully'.format(acp_name))

    def Show_ACP_Rule(self):
        self.Get_ACP()

        # Container UUID
        acp = input('input ACP ID :')
        container_ID = self.ACP_Dict[acp]
        print(container_ID)

        host_api_uri = "https://" + self.FMC_IP + "/api/fmc_config/v1/domain/" + self.DOMAIN_UUID + "/policy/accesspolicies/" + container_ID + "/accessrules"

        response = requests.get(host_api_uri, headers=self.HEADER_JSON,verify=False)
        print(response.status_code)
        temp = json.loads(response.text)
        print(temp)




    def Test(self):
        temp = []
        for i in range(3):
            a = {
                  "action": "ALLOW",
                  "enabled": 'true',
                  "type": "AccessRule",
                  "name": "A{}".format(i),
                  "sendEventsToFMC": 'false',
                  "id": "accessRuleUUID1",
                  "sourceZones": {
                    "objects": [
                      {
                        "name": "INSIDE",
                        "id": "700407d4-283d-11ee-a3b1-c5374fdbb789",
                        "type": "SecurityZone"
                      }
                    ]
                  },
                  "destinationZones": {
                    "objects": [
                      {
                        "name": "OUTSIDE",
                        "id": "998434a2-27c1-11ee-a3b1-c5374fdbb789",
                        "type": "SecurityZone"
                      }
                    ]
                  },
                "sourceNetworks": {
                    "objects": [
                        {
                            "name": "8.8.8.8",
                            "id": "00000000-0000-0ed3-0000-004294979088",
                            "type": "Host"
                        }
                    ]
                },
                "destinationNetworks": {
                    "objects": [
                        {
                            "name": "test",
                            "id": "00000000-0000-0ed3-0000-004294994565",
                            "type": "Host"
                        }
                    ]
                }
            }

            temp.append(a)

        # Container UUID
        acp = input('input ACP ID :')
        container_ID = self.ACP_Dict[acp]
        print(container_ID)

        data = json.dumps(temp)

        host_api_uri = "https://" + self.FMC_IP + "/api/fmc_config/v1/domain/" + self.DOMAIN_UUID + "/policy/accesspolicies/" + container_ID + "/accessrules?bulk=true&section=mandatory"

        response = requests.post(host_api_uri,headers=self.HEADER_JSON,data=data,verify=False)

        print(response.content)














    '''
            for num in range(len(temp['items'])):
                device_id_list.append(temp['items'][num]['id'])
                device_name_list.append(temp['items'][num]['name'])
    '''

    #
#        device_name_list.append()

#        print('Device ID : {}, Device Name : {}'.format(temp['items'][0]['id'],temp['items'][0]['name'])) # Device UUID == Container UUID







    def Create_object_host(self):
    #엑셀파일경로 입력하세요
        csvFilePath = 'C:/Users/ykk56/Git_Test/FMC/host_obj.csv'

        with open(csvFilePath, encoding='utf-8-sig') as csvf:
           csvReader = csv.DictReader(csvf)

           for rows in csvReader:
              print(rows)
              if rows['type'] == "Host":
                 self.host.append(rows)

        host_payload = json.dumps(self.host)

        print(host_payload)

        host_api_uri = "https://" + self.FMC_IP + "/api/fmc_config/v1/domain/" + self.DOMAIN_UUID + "/object/hosts?bulk=true"
        headers = {'Content-Type': 'application/json', 'x-auth-access-token': self.access_token}

        response = requests.request("POST", host_api_uri, headers=headers, data=host_payload, verify=False)
        print(response.content)


    def Create_object_range(self):
    #엑셀파일경로 입력하세요
        csvFilePath = 'C:/Users/ykk56/Git_Test/FMC/range_obj.csv'

        with open(csvFilePath, encoding='utf-8-sig') as csvf:
           csvReader = csv.DictReader(csvf)

           for rows in csvReader:
              print(rows)
              if rows['type'] == "Range":
                 self.host.append(rows)

        host_payload = json.dumps(self.host)

        print(host_payload)

        host_api_uri = "https://" + self.FMC_IP + "/api/fmc_config/v1/domain/" + self.DOMAIN_UUID + "/object/ranges?bulk=true"
        headers = {'Content-Type': 'application/json', 'x-auth-access-token': self.access_token}

        response = requests.request("POST", host_api_uri, headers=headers, data=host_payload, verify=False)
        print(response.content)

    def Create_object_network(self):
    #엑셀파일경로 입력하세요
        csvFilePath = 'C:/Users/ykk56/Git_Test/FMC/network_obj.csv'

        with open(csvFilePath, encoding='utf-8-sig') as csvf:
           csvReader = csv.DictReader(csvf)

           for rows in csvReader:
              print(rows)
              if rows['type'] == "Network":
                 self.host.append(rows)

        host_payload = json.dumps(self.host)

        print(host_payload)

        host_api_uri = "https://" + self.FMC_IP + "/api/fmc_config/v1/domain/" + self.DOMAIN_UUID + "/object/networks?bulk=true"
        headers = {'Content-Type': 'application/json', 'x-auth-access-token': self.access_token}

        response = requests.request("POST", host_api_uri, headers=headers, data=host_payload, verify=False)
        print(response.content)


    def Create_object_port(self):
    #엑셀파일경로 입력하세요
        csvFilePath = 'C:/Users/ykk56/Git_Test/FMC/port_obj.csv'

        with open(csvFilePath, encoding='utf-8-sig') as csvf:
           csvReader = csv.DictReader(csvf)

           for rows in csvReader:


             self.host.append(rows)

        host_payload = json.dumps(self.host)

        print(host_payload)

        host_api_uri = "https://" + self.FMC_IP + "/api/fmc_config/v1/domain/" + self.DOMAIN_UUID + "/object/protocolportobjects?bulk=true"
        headers = {'Content-Type': 'application/json', 'x-auth-access-token': self.access_token}

        response = requests.request("POST", host_api_uri, headers=headers, data=host_payload, verify=False)
        print(response.content)

    def Create_FtdNatRule(self):

        temp_name = input("Input Natrulename: ")
        host_api_uri = 'https://' + self.FMC_IP + '/api/fmc_config/v1/domain/' + self.DOMAIN_UUID + '/policy/ftdnatpolicies'

        headers = {'Content-Type': 'application/json', 'x-auth-access-token': self.access_token}
        data = {
            "type": "FTDNatPolicy",
            "name": "{}".format(temp_name),
            "description": "nat policy for testing rest api"
        }
        host_payload = json.dumps(data)

        response = requests.request("POST", host_api_uri, data=host_payload, headers=headers, verify=False)
        print(response.content)
        print(response.status_code)

    def Get_Object_ID(self):
        Object_UUID = []
        # GEt OBject ID
        host_api_uri = 'https://'+ self.FMC_IP +'/api/fmc_config/v1/domain/' + self.DOMAIN_UUID + '/object/hosts?offset=0&limit=1000'
        headers = {'accept': 'application/json', 'x-auth-access-token': self.access_token}
        response = requests.request("GET", host_api_uri, headers=headers, verify=False)

        a = json.loads(response.text)

        for i in a['items']:

            self.Source_Object_NAME.append(i['name'])
            self.Source_Object_ID.append(i['id'])
            self.Source_Object_Dict = dict(zip(self.Source_Object_NAME,self.Source_Object_ID))


        host_api_uri = 'https://' + self.FMC_IP + '/api/fmc_config/v1/domain/' + self.DOMAIN_UUID + '/object/hosts?offset=1000&limit=2000'
        headers = {'accept': 'application/json', 'x-auth-access-token': self.access_token}
        response = requests.request("GET", host_api_uri, headers=headers, verify=False)

        a = json.loads(response.text)

        for i in a['items']:
            self.Source_Object_NAME.append(i['name'])
            self.Source_Object_ID.append(i['id'])
            self.Source_Object_Dict = dict(zip(self.Source_Object_NAME, self.Source_Object_ID))


        host_api_uri = 'https://' + self.FMC_IP + '/api/fmc_config/v1/domain/' + self.DOMAIN_UUID + '/object/hosts?offset=2000&limit=3000'
        headers = {'accept': 'application/json', 'x-auth-access-token': self.access_token}
        response = requests.request("GET", host_api_uri, headers=headers, verify=False)

        a = json.loads(response.text)


        for i in a['items']:
            self.Source_Object_NAME.append(i['name'])
            self.Source_Object_ID.append(i['id'])
            self.Source_Object_Dict = dict(zip(self.Source_Object_NAME, self.Source_Object_ID))

        print(self.Source_Object_Dict)


        '''
        
        for key,value in self.Source_Object_Dict.items():
            print(key) # 요걸 name에
            print(value) # 요걸 id에
        '''


    def Create_Autonat(self):
        # get ftd natruleID
        host_api_uri = "https://" + self.FMC_IP +'/api/fmc_config/v1/domain/' + self.DOMAIN_UUID + "/policy/ftdnatpolicies"
        headers = {'Content-Type': 'application/json', 'x-auth-access-token': self.access_token}
        response = requests.request("GET", host_api_uri, headers=headers, verify=False)

        a = json.loads(response.content)



        load_wb = load_workbook('C:/Users/Myamori/PycharmProjects/2023_python/Test/autonat.xlsx')

        load_ws = load_wb['Sheet1']

        nat_rule_src = []
        nat_rule_dst = []

        for column in load_ws['A']:
            nat_rule_src.append(column.value)

        for column in load_ws['B']:
            nat_rule_dst.append(column.value)

        temp_name = input("룰 넣을 NATPolicy name 입력 : ")
        temp_id = ''

        for i in a['items']:
            if temp_name == i['name'] :
                temp_id = i['id']


        data_list = []

        for i in range(0,len(nat_rule_src)) :
            print(nat_rule_src[i])
            print(self.Source_Object_Dict[nat_rule_src[i]])
            print(nat_rule_dst[i])
            print(self.Source_Object_Dict[nat_rule_dst[i]])

            data_list.append({
                "type": "FTDAutoNatRule",
                "originalNetwork": {
                    "type": "Hosts",
                    "name": "{}".format(nat_rule_src[i]),
                    "id": "{}".format(self.Source_Object_Dict[nat_rule_src[i]])
                },
                "serviceProtocol": "TCP",
                "originalPort": 123,
                "translatedNetwork": {
                    "type": "Hosts",
                    "name": "{}".format(nat_rule_dst[i]),
                    "id": "{}".format(self.Source_Object_Dict[nat_rule_dst[i]])
                },
                "translatedPort": 234,
                "interfaceInTranslatedNetwork": False,
                "dns": False,
                "routeLookup": False,
                "noProxyArp": False,
                "netToNet": False,
                "fallThrough": False,
                "natType": "STATIC",
            })

        host_api_uri = "https://" + self.FMC_IP +'/api/fmc_config/v1/domain/' + self.DOMAIN_UUID + '/policy/ftdnatpolicies/'+ temp_id +'/autonatrules?bulk=true'
        headers = {'Content-Type': 'application/json', 'x-auth-access-token': self.access_token}

        host_payload = json.dumps(data_list)
        response = requests.request("POST", host_api_uri, data=host_payload, headers=headers, verify=False)
        a = response.status_code
        print(a)

    def Check_object_dup(self):
        host_api_uri = 'https://' + self.FMC_IP + '/api/fmc_config/v1/domain/' + self.DOMAIN_UUID + '/object/hosts?offset=0&limit=1000'
        headers = {'accept': 'application/json', 'x-auth-access-token': self.access_token}
        response = requests.request("GET", host_api_uri, headers=headers, verify=False)
        a = json.loads(response.text)

        for i in a['items']:
            print(i['id'])
            host_api_uri = 'https://' + self.FMC_IP + '/api/fmc_config/v1/domain/' + self.DOMAIN_UUID + '/object/hosts/{}'.format(i['id'])
            response = requests.request("DELETE", host_api_uri, headers=headers, verify=False)



# IP , ID , PW 입력하세요
FMC = FMC_TEST('192.168.80.33','admin','Ringnet01!')

#FMC.Get_ACP()
#FMC = FMC_TEST(input('FMC IP :'),input('Username :'),input('Password :'))


while True:
    input_value = input('Show device list: d\n'
                        'Show ACP: a\n'
                        'Show Security_Zone : SZ\n'
                        'Show ACP Rule : SAR\n'
                        'Create Hosts_Obj : CHO\n'
                        'Create Ranges_Obj : CRO\n'
                        'TEST : T\n'
                        'Create ACP: CA\n'
                        'Exit : q\n'
                        'TEST2 :T2\n'
                        'input :')

    if input_value == 'CHO':
        FMC.Create_object_host()
    if input_value == 'CRO':
        FMC.Create_object_range()
    if input_value == 'CNO':
        FMC.Create_object_network()
    if input_value == 'CPO':
        FMC.Create_object_port()
    if input_value == 'SZ':
        FMC.Show_SecurityZone()
    if input_value == 't':
        print(FMC.access_token)
    if input_value == 'T':
        FMC.Test()
    if input_value == 'SAR':
        FMC.Show_ACP_Rule()
    if input_value == 'q':
        break

    if input_value == 'd':
        FMC.Get_DeviceList()

    if input_value == 'a':
        FMC.Show_ACP()

    if input_value == 'CA':
        FMC.Create_ACP()



    #FMC.Create_object()
    #FMC.Get_Object_ID()

    #FMC.Check_object_dup()

    #FMC.Create_FtdNatRule()
    #FMC.Create_Autonat()
    #print(FMC.Source_Object_Dict)





