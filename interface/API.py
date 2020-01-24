import base64
import binascii
import logging
from jinja2 import Template
import requests
import xmltodict
import json
from zeep import Client,helpers
import hashlib
from requests.auth import HTTPBasicAuth

from accounts.utils import config_logging
from transactions.models import ProvidersToken, Operator
from transactions.enums import ResponceCodeTypes as codes , ResponseTypes

MCI_token = ""


class Parameter:
    def __init__(self, name, value):
        self.name = name
        self.value = value


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
        headers = {'Content-Type': 'application/json', }
        api_username = self.behsa_charge_username
        data = '{\'TelNum\':' + str(tel_num) + ',\'TelCharger\':' + str(tel_charger) + ',\'Amount\': ' + str(
            amount) + ',\'ChargeType\':' + str(charge_type) + ',\'BrokerId\':' + api_username + '}'
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
        headers = {'Content-Type': 'application/json', }
        api_username = self.behsa_package_username
        data = '{\'TelNum\':' + str(tel_num) + ',\'TelCharger\':' + str(tel_charger) + ',\'Amount\': ' + str(
            amount) + ',\'PackageType\':' + str(packageType) + ',\'BrokerId\':' + api_username + '}'
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
        headers = {'Content-Type': 'application/json', }
        api_username = self.behsa_charge_username
        data = '{\'BrokerId\':' + api_username + '}'
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

    def behsa_subscriber_charge_credit(self,TelNum):
        api_url = self.behsa_url + 'Topup/QueryBalance'
        headers = {'Content-Type': 'application/json', }
        api_username = self.behsa_charge_username
        data = '{\'TelNum\':' + str(TelNum) + '}'
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

    def behsa_subscriber_package_quata(self,TelNum):
        api_url = self.behsa_url + 'Topup/QueryQuata'
        headers = {'Content-Type': 'application/json', }
        api_username = self.behsa_package_username
        data = '{\'TelNum\':' + str(TelNum) + '}'
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

    def behsa_subscriber_type(self,TelNum):
        api_url = self.behsa_url + 'Topup/QuerySimType'
        headers = {'Content-Type': 'application/json', }
        api_username = self.behsa_charge_username
        data = '{\'TelNum\':' + str(TelNum) + '}'
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

    def behsa_package_credit(self):
        api_url = self.behsa_url + 'Topup/RemainCreditInquiryPackage'
        headers = {'Content-Type': 'application/json', }
        api_username = self.behsa_package_username
        data = '{\'BrokerId\':' + api_username + '}'
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

    def behsa_package_query(self):
        api_url = self.behsa_url + 'Topup/PackagesListQuery'
        headers = {'Content-Type': 'application/json', }
        api_username = self.behsa_package_username
        data = {}
        response = requests.post(api_url, headers=headers, data=data,
                                 auth=(api_username, self.behsa_generated_pass(api_username)))
        res = json.loads(response.text)
        try:
            response_type = res['ResponseType']
            response_description = res['ResponseDesc']
        except:
            return 0, res
        if int(response_type) == -2:
            self.token()
            response = requests.post(api_url, headers=headers, data=data,
                                     auth=(api_username, self.behsa_generated_pass(api_username)))
            res = json.loads(response.text)
            try:
                response_type = res['ResponseType']
                response_description = res['ResponseDesc']
            except:
                return 0, res
        if int(response_type) < 0:
            logger = config_logging(logging.INFO, 'debug.log', 'debug')
            logger.propagate = False
            content = '***Behsa error*** ResponseType: ' + str(response_type) + ', ResponseDesc: ' + str(
                response_description)
            logger.info(content)
        return response_type, response_description

    def behsa_generated_pass(self, username):
        providerToken = ProvidersToken.objects.get(provider=Operator.MCI.value)
        return self.behsa_hash(username.upper() + '|' + self.behsa_password + '|' + providerToken.token)

    def behsa_charge_status(self, provider_id, TelNum, Bank):
        api_url = self.behsa_url + 'Topup/ChargeStatusInquery'
        headers = {'Content-Type': 'application/json', }
        api_username = self.behsa_charge_username
        data = '{\'ProviderId\':' + str(provider_id) + ',\'Bank\':' + str(Bank) + ',\'BrokerId\': ' + str(
            api_username) + ',\'TelNum\':' + str(TelNum) + '}'
        response = requests.post(api_url, headers=headers, data=data,
                                 auth=(api_username, self.behsa_generated_pass(api_username)))
        res = json.loads(response.text)
        response_type = res['ResponseType']
        if int(response_type) == -2:
            self.token()
            response = requests.post(api_url, headers=headers, data=data,
                                     auth=(api_username, self.behsa_generated_pass(api_username)))
            res = json.loads(response.text)
            response_type = res['ResponseType']
        if int(response_type) < 0:
            logger = config_logging(logging.INFO, 'debug.log', 'debug')
            logger.propagate = False
            content = '***Behsa error*** ResponseType: ' + str(response_type) + ', ResponseDesc: ' + str(
                res['ResponseDesc'])
            logger.info(content)
        return res

    def behsa_package_status(self, provider_id, TelNum, Bank):
        api_url = self.behsa_url + 'Topup/PackageActivationStatus'
        headers = {'Content-Type': 'application/json', }
        api_username = self.behsa_package_username
        data = '{\'ProviderID\':' + str(provider_id) + ',\'BankCode\':' + str(Bank) + ',\'BrokerId\': ' + str(
            api_username) + ',\'TelNum\':' + str(TelNum) + '}'
        response = requests.post(api_url, headers=headers, data=data,
                                 auth=(api_username, self.behsa_generated_pass(api_username)))
        res = json.loads(response.text)
        response_type = res['ResponseType']
        if int(response_type) == -2:
            self.token()
            response = requests.post(api_url, headers=headers, data=data,
                                     auth=(api_username, self.behsa_generated_pass(api_username)))
            res = json.loads(response.text)
            response_type = res['ResponseType']
        if int(response_type) < 0:
            logger = config_logging(logging.INFO, 'debug.log', 'debug')
            logger.propagate = False
            content = '***Behsa error*** ResponseType: ' + str(response_type) + ', ResponseDesc: ' + str(
                res['ResponseDesc'])
            logger.info(content)
        return res

    @staticmethod
    def behsa_hash(hash_string):
        byte_hash = hash_string.encode()
        md5hash = hashlib.md5(byte_hash).hexdigest()
        return md5hash.replace("-", "")


# class EWays:
#     eways_pass = '19K1*57e51'
#     tag1 = 'req'
#     tag2 = 'tem'
#     xmlns1 ='http://NewCore.Eways.ir/Webservice/Request.asmx'
#     xmlns2 = 'http://tempuri.org/'
#     eways_url_1 = 'http://core.eways.ir/WebService/Request.asmx'
#     eways_url_2 = 'http://core.eways.ir/WebService/BackEndRequest.asmx'
#
#     def ewaysreqrypei(self,action, eways_url, params , tag , xlmns):
#         headers = {'content-type': 'text/xml'}
#
#         template = Template("""<{{tag}}:{{name}}>{{value}}</{{tag}}:{{name}}>""")
#
#         requestTemp = Template("""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:{{tag}}="{{xlmns}}">
#    <soapenv:Header/>
#    <soapenv:Body>
#       <{{tag}}:{{action}}>
# {{parameter}}
#       </{{tag}}:{{action}}>
#    </soapenv:Body>
# </soapenv:Envelope>""")
#
#         parameters = ""
#         for x in params:
#             parameters = parameters + template.render(name=x.name, value=x.value , tag = tag)
#         body = requestTemp.render(action=action, parameter=parameters , tag=tag , xlmns = xlmns)
#         return requests.post(eways_url, data=body, headers=headers, verify=False).content
#
#
#
#     def call_sale(self, requestID):
#         response = self.ewaysreqrypei('GetProduct', self.eways_url_1, [Parameter("TransactionID", requestID),
#                                                                           Parameter("UserName", self.eways_pass)],self.tag1 , self.xmlns1)
#         return response
#
#     def exe_sale(self, requestID , productType,Count,Mobile):
#         response = self.ewaysreqrypei('RequestPins', self.eways_url_2, [Parameter("RequestID", requestID),
#                                                                        Parameter("SitePassword", self.eways_pass),
#                                                                        Parameter("ProductType", productType),
#                                                                        Parameter("Count", Count),
#                                                                           Parameter("Mobile", Mobile)],self.tag2 , self.xmlns2)
#         return response
#
#     def get_status(self, TransactionID,RequestID):
#         response = self.ewaysreqrypei('GetStatus', self.eways_url_1, [Parameter("TransactionID", TransactionID),
#                                                                           Parameter("RequestID", RequestID)],self.tag1 , self.xmlns1)
#         return response

class EWays:
    eways_pass = '19K1*57e51'
    eways_url_1 = 'http://core.eways.ir/WebService/Request.asmx?wsdl'
    eways_url_2 = "http://core.eways.ir/WebService/BackEndRequest.asmx?wsdl"

    def call_sale(self, TransactionID):
        client = Client(self.eways_url_1)
        response = client.service.GetProduct(TransactionID=TransactionID, UserName=self.eways_pass)
        return self.eways_response_mapper(response, True)

    def exe_sale(self, requestID, productType, Count,Mobile):

        client = Client(self.eways_url_2)
        response = client.service.RequestPins(RequestID=requestID,SitePassword=self.eways_pass, ProductType=productType,Count=Count,
                                              Mobile=Mobile)
        return self.eways_response_mapper(response[0], False)

    def exe_sale_test(self, requestID, productType, Count,Mobile):

        client = Client(self.eways_url_2)
        response = client.service.RequestPins(RequestID=requestID,SitePassword=self.eways_pass, ProductType=productType,Count=Count,
                                              Mobile=Mobile)
        return response[0]

    def get_status(self, TransactionID,RequestID):
        client = Client(self.eways_url_1)
        response = client.service.GetStatus(TransactionID=TransactionID,RequestID=RequestID)
        try:
            res = json.loads(json.dumps(helpers.serialize_object(response)))[0]
            return True, res
        except Exception:
            return False, ''

    def eways_response_mapper(self, response, callsale):
        print(response)
        print(response['Status'])
        print(type(response))
        try:
            if response['Status'] in[0, 40, 114, 400, 500, 600, 700, 1100]:
                if callsale:
                    res = json.loads(json.dumps(xmltodict.parse(response['Result'])))
                    for i in res['Eways']['Requirements']['Requirement']:
                        if i['@ID'] == 'UUID':
                            return codes.successful, i['#text']
                else:
                    return codes.successful, response['Message']
            elif response['Status'] in [36, 37, 42, 404, 405, 406, 408, 501, 502, 504, 507, 508, 604, 605, 606, 608, 609, 804, 809, -2, -3]:
                return ResponseTypes.SYSTEMERROR.value, response['Message']
            elif response['Status'] in [509]:
                return ResponseTypes.ERRORCHARGE.value,response['Message']
            else:
                return ResponseTypes.REFERTODESC.value, str(response['Status']) + ' : ' + response['Message']
        except Exception as e:
            print(e)
            return ResponseTypes.REFERTODESC.value, ResponseTypes.farsi(ResponseTypes.SYSTEMERROR.value)

