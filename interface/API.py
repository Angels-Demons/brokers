import logging

import requests
import json
import hashlib
from requests.auth import HTTPBasicAuth

from accounts.utils import config_logging


class MCI:
    behsa_url = "http://10.19.252.21:5003/rest/"
    behsa_username = ''
    behsa_password = ''
    MCI_token = ''
    broker_id = ''

    def token(self):
        header = {'Content-type': 'application/json', 'Accept': '*/*'}
        response = requests.get(url=self.behsa_url + 'Token', headers=header)
        res = json.loads(response.text)
        try:
            if res['ResponseType'] == 0:
                self.MCI_token = res['TokenID']
                return True
        except:
            logger = config_logging(logging.INFO, 'debug.log', 'debug')
            logger.propagate = False
            logger.info('***Exception in refreshing Behsa token***')
            return False

    def call_sale(self, tel_num, tel_charger, amount, charge_type):
        header = {'Content-type': 'application/json', 'Accept': '*/*'}
        data = {
            'TelNum': tel_num,
            'TelCharger': tel_charger,
            'Amount': amount,
            'ChargeType': charge_type,
            'BrokerId': self.broker_id
        }
        response = requests.post(url=self.behsa_url + 'Topup/CallSaleProvider', data=data,
                                 auth=HTTPBasicAuth(self.behsa_username, self.behsa_generated_pass), headers=header)
        if response.status_code == 401:
            self.token()
            response = requests.post(url=self.behsa_url + 'Topup/CallSaleProvider', data=data,
                                     auth=HTTPBasicAuth(self.behsa_username, self.behsa_generated_pass), headers=header)
        res = json.loads(response.text)
        response_type = res['ResponseType']
        response_description = res['ResponseDesc']
        if response_type < 0:
            logger = config_logging(logging.INFO, 'debug.log', 'debug')
            logger.propagate = False
            content = '***Behsa error*** ResponseType: ' + str(response_type) + ', ResponseDesc: ' + str(
                response_description)
            logger.info(content)
        return response_type, response_description

    def exe_sale(self, provider_id, bank_code, card_no, card_type):
        header = {'Content-type': 'application/json', 'Accept': '*/*'}
        data = {
            'ProviderID': provider_id,
            'BankCode': bank_code,
            'CardNo': card_no,
            'CardType': card_type
        }
        response = requests.post(url=self.behsa_url + 'Topup/ExecSaleProvider', data=data,
                                 auth=HTTPBasicAuth(self.behsa_username, self.behsa_generated_pass), headers=header)
        if response.status_code == 401:
            self.token()
            response = requests.post(url=self.behsa_url + 'Topup/CallSaleProvider', data=data,
                                     auth=HTTPBasicAuth(self.behsa_username, self.behsa_generated_pass), headers=header)
        res = json.loads(response.text)
        response_type = res['ResponseType']
        response_description = res['ResponseDesc']
        if response_type < 0:
            logger = config_logging(logging.INFO, 'debug.log', 'debug')
            logger.propagate = False
            content = '***Behsa error*** ResponseType: ' + str(response_type) + ', ResponseDesc: ' + str(
                response_description)
            logger.info(content)
        return response_type, response_description

    def charge_status(self, broker_id, tel_num, provider_id, bank):
        header = {'Content-type': 'application/json', 'Accept': '*/*'}
        data = {
            'BrokerId': broker_id,
            'TelNum': tel_num,
            'ProviderId': provider_id,
            'Bank': bank
        }
        response = requests.post(url=self.behsa_url + 'Topup/ChargeStatusInquery', data=data,
                                 auth=HTTPBasicAuth(self.behsa_username, self.behsa_generated_pass), headers=header, )
        if response.status_code == 401:
            self.token()
            response = requests.post(url=self.behsa_url + 'Topup/CallSaleProvider', data=data,
                                     auth=HTTPBasicAuth(self.behsa_username, self.behsa_generated_pass), headers=header)
        res = json.loads(response.text)
        response_type = res['ResponseType']
        response_description = res['ResponseDesc']
        if response_type < 0:
            logger = config_logging(logging.INFO, 'debug.log', 'debug')
            logger.propagate = False
            content = '***Behsa error*** ResponseType: ' + str(response_type) + ', ResponseDesc: ' + str(
                response_description)
            logger.info(content)
        return response_type, response_description

    @property
    def behsa_generated_pass(self):
        return self.behsa_hash(self.behsa_username.upper() + '|' + self.behsa_password + '|' + self.MCI_token)

    @staticmethod
    def behsa_hash(hash_string):
        byte_hash = hash_string.encode()
        return str(hashlib.md5(byte_hash))
