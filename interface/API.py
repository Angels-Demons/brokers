import base64
import binascii
import logging

import requests
import json
import hashlib
from requests.auth import HTTPBasicAuth

from accounts.utils import config_logging
from transactions.models import ProvidersToken, Operator

MCI_token = ""


class MCI:
    behsa_url = "http://10.19.252.21:5003/Rest/"
    behsa_charge_username = '13001053'
    behsa_package_username = '13001447'
    behsa_password = 'E@123456'

    def token(self):
        header = {'Content-type': 'application/json', 'Accept': '*/*'}
        data = {}
        response = requests.post(url=self.behsa_url + 'Token', headers=header, data=data)
        res = json.loads(response.text)
        try:
            if int(res['ResponseType']) == 0:
                prToken = ProvidersToken.objects.get(provider=Operator.MCI.value)
                prToken.update_token(str(res['TokenID']))
                return True
        except Exception as e:
            logger = config_logging(logging.INFO, 'debug.log', 'debug')
            logger.propagate = False
            logger.info('***Exception in refreshing Behsa token***')
            return False

    def charge_call_sale(self, tel_num, tel_charger, amount, charge_type):
        api_url = self.behsa_url + 'Topup/CallSaleProvider'
        headers = {'Content-Type': 'application/json',}
        api_username = self.behsa_charge_username
        data = '{\'TelNum\':'+str(tel_num)+',\'TelCharger\':' +str(tel_charger) +',\'Amount\': '+str(amount)+',\'ChargeType\':' +str(charge_type)+ ',\'BrokerId\':' + api_username +'}'
        response = requests.post(api_url , headers=headers, data=data,
                                 auth=(api_username,self.behsa_generated_pass(api_username)))
        res = json.loads(response.text)
        response_type = res['ResponseType']
        response_description = res['ResponseDesc']

        if int(response_type) == -2:
            self.token()
            response = requests.post(api_url, headers=headers, data=data,
                                     auth=(api_username, self.behsa_generated_pass(api_username)))
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

    def charge_exe_sale(self, provider_id, bank_code, card_no, card_type):
        api_url = self.behsa_url + 'Topup/ExecSaleProvider'
        headers = {'Content-Type': 'application/json', }
        api_username = self.behsa_charge_username
        data = '{\'ProviderID\':' + str(provider_id) + ',\'BankCode\':' + str(bank_code) + ',\'CardNo\': ' + str(
            card_no) + ',\'CardType\':' + str(card_type) + '}'
        response = requests.post(api_url, headers=headers, data=data,
                                 auth=(api_username, self.behsa_generated_pass(api_username)))

        res = json.loads(response.text)
        response_type = res['ResponseType']
        response_description = res['ResponseDesc']

        if int(response_type) == -2:
            self.token()
            response = requests.post(api_url, headers=headers, data=data,
                                     auth=(api_username, self.behsa_generated_pass(api_username)))
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

    def package_call_sale(self, tel_num, tel_charger, amount, packageType):
        api_url = self.behsa_url + 'Topup/CallSaleProviderPackage'
        headers = {'Content-Type': 'application/json',}
        api_username = self.behsa_package_username
        data = '{\'TelNum\':'+str(tel_num)+',\'TelCharger\':' +str(tel_charger) +',\'Amount\': '+str(amount)+',\'PackageType\':' +str(packageType)+ ',\'BrokerId\':' + api_username +'}'
        response = requests.post(api_url , headers=headers, data=data,
                                 auth=(api_username,self.behsa_generated_pass(api_username)))
        res = json.loads(response.text)
        response_type = res['ResponseType']
        response_description = res['ResponseDesc']

        if int(response_type) == -2:
            self.token()
            response = requests.post(api_url, headers=headers, data=data,
                                     auth=(api_username, self.behsa_generated_pass(api_username)))
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
        api_url = self.behsa_url + 'Topup/ExecSaleProviderPackage'
        headers = {'Content-Type': 'application/json', }
        api_username = self.behsa_package_username
        data = '{\'ProviderID\':' + str(provider_id) + ',\'BankCode\':' + str(bank_code) + ',\'CardNo\': ' + str(
            card_no) + ',\'CardType\':' + str(card_type) + '}'
        response = requests.post(api_url, headers=headers, data=data,
                                 auth=(api_username, self.behsa_generated_pass(api_username)))

        res = json.loads(response.text)
        response_type = res['ResponseType']
        response_description = res['ResponseDesc']

        if int(response_type) == -2:
            self.token()
            response = requests.post(api_url, headers=headers, data=data,
                                     auth=(api_username, self.behsa_generated_pass(api_username)))
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



    def behsa_charge_credit(self):
        api_url = self.behsa_url + 'Topup/RemainCreditInquiry'
        headers = {'Content-Type': 'application/json',}
        api_username = self.behsa_charge_username
        data = '{\'BrokerId\':' + api_username +'}'
        response = requests.post(api_url , headers=headers, data=data,
                                 auth=(api_username,self.behsa_generated_pass(api_username)))
        res = json.loads(response.text)
        response_type = res['ResponseType']
        response_description = res['ResponseDesc']

        if int(response_type) == -2:
            self.token()
            response = requests.post(api_url, headers=headers, data=data,
                                     auth=(api_username, self.behsa_generated_pass(api_username)))
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

    def behsa_package_credit(self):
        api_url = self.behsa_url + 'Topup/RemainCreditInquiry'
        headers = {'Content-Type': 'application/json',}
        api_username = self.behsa_package_username
        data = '{\'BrokerId\':' + api_username +'}'
        response = requests.post(api_url , headers=headers, data=data,
                                 auth=(api_username,self.behsa_generated_pass(api_username)))
        res = json.loads(response.text)
        response_type = res['ResponseType']
        response_description = res['ResponseDesc']

        if int(response_type) == -2:
            self.token()
            print("**************** -2 error")
            response = requests.post(api_url, headers=headers, data=data,
                                     auth=(api_username, self.behsa_generated_pass(api_username)))
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

    def behsa_package_query(self):
        api_url = self.behsa_url + 'Topup/PackagesListQuery'
        headers = {'Content-Type': 'application/json',}
        api_username = self.behsa_package_username
        data = {}
        response = requests.post(api_url , headers=headers, data=data,
                                 auth=(api_username,self.behsa_generated_pass(api_username)))
        res = json.loads(response.text)
        response_type = res['ResponseType']
        response_description = res['ResponseDesc']

        if int(response_type) == -2:
            self.token()
            print("**************** -2 error")
            response = requests.post(api_url, headers=headers, data=data,
                                     auth=(api_username, self.behsa_generated_pass(api_username)))
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

    def behsa_generated_pass(self,username):
        providerToken = ProvidersToken.objects.get(provider=Operator.MCI.value)
        return self.behsa_hash(username.upper() + '|' + self.behsa_password + '|' + providerToken.token)

    @staticmethod
    def behsa_hash(hash_string):
        byte_hash = hash_string.encode()
        md5hash = hashlib.md5(byte_hash).hexdigest()
        return md5hash.replace("-", "")

    # @staticmethod
    # def localBasic(username, password):
    #     userpass = username + ":" + password
    #     encodedBytes = base64.b64encode(userpass.encode("utf-8"))
    #     encodedStr = "Basic " + str(encodedBytes, "utf-8")
    #     return encodedStr
