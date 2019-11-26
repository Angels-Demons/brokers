import requests
import json
from django.shortcuts import redirect
import hashlib
from requests.auth import HTTPBasicAuth

url_behsa = "http://10.19.252.21:5003/rest/"
behsa_username = ''
behsa_password = ''
behsa_password_upper = ''
MCI_token = ''
broker_id = ''


class MCI:
    @staticmethod
    def token():
        headers = {'Content-type': 'application/json', 'Accept': '*/*'}
        response = requests.get(url=url_behsa+'Token',headers=headers)
        res = json.loads(response.text)
        try:
            if res['ResponseType'] == 0:
                MCI_token = res['TokenID']
                return True
        except:
            return False

    @staticmethod
    def call_sale(TelNum,TelCharger,Amount,ChargeType):
        headers = {'Content-type': 'application/json', 'Accept': '*/*'}
        data = {
            'TelNum':TelNum,
            'TelCharger':TelCharger,
            'Amount':Amount,
            'ChargeType':ChargeType,
            'BrokerId':broker_id
        }
        response = requests.post(url=url_behsa+'Topup/CallSaleProvider',data=data,auth = HTTPBasicAuth(behsa_username,Create_behsa_pass()),headers=headers)
        res = json.loads(response.text)
        response_type = res['ResponseType']
        response_description = res['ResponseDesc']
        return response_type, response_description


    @staticmethod
    def exe_sale(ProviderID,BankCode,CardNo,CardType):
        headers = {'Content-type': 'application/json', 'Accept': '*/*'}
        data = {
            'ProviderID':ProviderID,
            'BankCode':BankCode,
            'CardNo':CardNo,
            'CardType':CardType
        }
        response = requests.post(url=url_behsa+'Topup/ExecSaleProvider',data=data,auth = HTTPBasicAuth(behsa_username,Create_behsa_pass()),headers=headers)
        res = json.loads(response.text)
        response_type = res['ResponseType']
        response_description = res['ResponseDesc']
        return response_type, response_description

    @staticmethod
    def charge_status(BrokerId,TelNum,ProviderId,Bank):
        headers = {'Content-type': 'application/json', 'Accept': '*/*'}
        data = {
            'BrokerId':BrokerId,
            'TelNum':TelNum,
            'ProviderId':ProviderId,
            'Bank':Bank
        }
        response = requests.post(url=url_behsa+'Topup/ChargeStatusInquery',data=data,auth = HTTPBasicAuth(behsa_username,Create_behsa_pass()),headers=headers)
        res = json.loads(response.text)
        response_type = res['ResponseType']
        response_description = res['ResponseDesc']
        return response_type, response_description






def Create_behsa_pass():
    return Behsa_hash(behsa_username+ '|' +behsa_password_upper+ '|' +MCI_token)

def Behsa_hash(hash_string):
    byte_hash = hash_string.encode()
    return str(hashlib.md5(byte_hash))

