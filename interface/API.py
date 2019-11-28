import binascii
import logging

import requests
import json
import hashlib
from requests.auth import HTTPBasicAuth

from accounts.utils import config_logging
from transactions.models import ProvidersToken, ProviderType

MCI_token = ""


class MCI:
    behsa_url = "http://10.19.252.21:5003/Rest/"
    behsa_username = '13001053'
    behsa_password = 'E@123456'
    MCI_token = "cd583b51ff44f1738b4256a7e3073b43"
    broker_id = '13001053'

    def token(self):
        print("******** Start Token Request ***** ")
        header = {'Content-type': 'application/json', 'Accept': '*/*'}
        data = {}
        response = requests.post(url=self.behsa_url + 'Token', headers=header, data=data)
        res = json.loads(response.text)
        try:
            if int(res['ResponseType']) == 0:
                print("******** Token Request : Successfully Get Token ***** ")
                prToken = ProvidersToken.objects.get(provider=ProviderType.MCI.value)
                prToken.update_token(str(res['TokenID']))
                return True
        except Exception as e:
            logger = config_logging(logging.INFO, 'debug.log', 'debug')
            logger.propagate = False
            logger.info('***Exception in refreshing Behsa token***')
            return False

    def charge_call_sale(self, tel_num, tel_charger, amount, charge_type):
        try:
            print("******** Start CallSale Request ***** ")
            header = {'Content-type': 'application/json'}
            data = {
                'TelNum': tel_num,
                'TelCharger': tel_charger,
                'Amount': amount,
                'ChargeType': charge_type,
                'BrokerId': self.broker_id
            }
            # auth = HTTPBasicAuth(self.behsa_username, self.behsa_generated_pass),
            url = self.behsa_url + 'Topup/CallSaleProvider'
            print("******** CallSale Request Sent ***** ")
            response = requests.post(url=url, data=data, headers=header)
            print("******** CallSale Request Executed ***** ")
            print("******** CallSale Response Text : ***** " + response.text)
            res = json.loads(response.text)
            print("******************** Behsa Result :"+response.text)
            response_type = res['ResponseType']
            response_description = res['ResponseDesc']

            if int(response_type) == -2:
                self.token()
                response = requests.post(url=self.behsa_url + 'Topup/CallSaleProvider', data=data,
                                         auth=HTTPBasicAuth(self.behsa_username, self.behsa_generated_pass), headers=header)
                res = json.loads(response.text)
                response_type = res['ResponseType']
                response_description = res['ResponseDesc']
            if int(response_type) < 0:
                logger = config_logging(logging.INFO, 'debug.log', 'debug')
                logger.propagate = False
                content = '***Behsa error*** ResponseType: ' + str(response_type) + ', ResponseDesc: ' + str(
                    response_description)
                logger.info(content)
        except Exception as e:
            print("*********** Exeption :" + str(e))
        return response_type, response_description

    def charge_exe_sale(self, provider_id, bank_code, card_no, card_type):
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
            response = requests.post(url=self.behsa_url + 'Topup/ExecSaleProvider', data=data,
                                     auth=HTTPBasicAuth(self.behsa_username, self.behsa_generated_pass), headers=header)
        res = json.loads(response.text)
        response_type = res['ResponseType']
        response_description = res['ResponseDesc']
        if int(response_type) < 0:
            logger = config_logging(logging.INFO, 'debug.log', 'debug')
            logger.propagate = False
            content = '***Behsa error*** ResponseType: ' + str(response_type) + ', ResponseDesc: ' + str(
                response_description)
            logger.info(content)
        return response_type, response_description

    def package_call_sale(self, tel_num, tel_charger, amount, package_type):
        header = {'Content-type': 'application/json', 'Accept': '*/*'}
        data = {
            'TelNum': tel_num,
            'TelCharger': tel_charger,
            'Amount': amount,
            'PackageType': package_type,
            'BrokerId': self.broker_id
        }
        response = requests.post(url=self.behsa_url + 'Topup/CallSaleProviderPackage', data=data,
                                 auth=HTTPBasicAuth(self.behsa_username, self.behsa_generated_pass), headers=header)
        res = json.loads(response.text)
        response_type = res['ResponseType']
        response_description = res['ResponseDesc']
        if int(response_type) == -2:
            self.token()
            response = requests.post(url=self.behsa_url + 'Topup/CallSaleProvider', data=data,
                                     auth=HTTPBasicAuth(self.behsa_username, self.behsa_generated_pass), headers=header)
            res = json.loads(response.text)
            response_type = res['ResponseType']
            response_description = res['ResponseDesc']
        if int(response_type) < 0:
            logger = config_logging(logging.INFO, 'debug.log', 'debug')
            logger.propagate = False
            content = '***Behsa error*** ResponseType: ' + str(response_type) + ', ResponseDesc: ' + str(
                response_description)
            logger.info(content)
        return response_type, response_description

    def package_exe_sale(self, provider_id, bank_code, card_no, card_type):
        header = {'Content-type': 'application/json', 'Accept': '*/*'}
        data = {
            'ProviderID': provider_id,
            'BankCode': bank_code,
            'CardNo': card_no,
            'CardType': card_type
        }
        response = requests.post(url=self.behsa_url + 'Topup/ExecSaleProviderPackage', data=data,
                                 auth=HTTPBasicAuth(self.behsa_username, self.behsa_generated_pass), headers=header)
        res = json.loads(response.text)
        response_type = res['ResponseType']
        response_description = res['ResponseDesc']
        if int(response_type) < 0:
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
        res = json.loads(response.text)
        response_type = res['ResponseType']
        response_description = res['ResponseDesc']
        if int(response_type) == -2:
            self.token()
            response = requests.post(url=self.behsa_url + 'Topup/CallSaleProvider', data=data,
                                     auth=HTTPBasicAuth(self.behsa_username, self.behsa_generated_pass), headers=header)
            res = json.loads(response.text)
            response_type = res['ResponseType']
            response_description = res['ResponseDesc']
        if int(response_type) < 0:
            logger = config_logging(logging.INFO, 'debug.log', 'debug')
            logger.propagate = False
            content = '***Behsa error*** ResponseType: ' + str(response_type) + ', ResponseDesc: ' + str(
                response_description)
            logger.info(content)
        return response_type, response_description

    @property
    def behsa_generated_pass(self):
        providerToken = ProvidersToken.objects.get(provider=ProviderType.MCI.value)
        return self.behsa_hash(self.behsa_username.upper() + '|' + self.behsa_password + '|' + providerToken.token)

    @staticmethod
    def behsa_hash(hash_string):
        byte_hash = hash_string.encode()
        md5hash = hashlib.md5(byte_hash).hexdigest()
        return md5hash.replace("-", "")
