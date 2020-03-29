import datetime
from time import sleep

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import transaction
# from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from accounts.views import BaseAPIView
from accounts.models import ChargeType
from interface.API import MCI, EWays
from accounts.models import Broker, OperatorAccess
from transactions.models import TopUp, PackageRecord, RecordState, Package
from transactions.serializers import PackageSerializer, OperatorAccessSerializer
from transactions.enums import ResponceCodeTypes as codes, Operator , ChargeType as chargecode , ResponseTypes

ACTIVE_DAYS = 360


def expired():
    t_delta = (datetime.datetime.now() - User.objects.first().date_joined).days
    if t_delta > ACTIVE_DAYS:
        return True


def search_mci_package(package, response):
    for res in response:
        if int(res['Package_Type']) == int(package.package_type):
            package.name = res['Package_Desc']
            package.description = res['Package_Desc']
            package.amount = int(res['Package_Cost'] or 999)
            package.system = int(res['Systems'] or 100)
            package.active = True
            package.save()
            return
    package.active = False
    package.save()


def update_mci_packages():
    print("************** Start Updating Packages")
    response_code, response_desc = MCI().behsa_package_query()
    if response_code == 0:
        all_mci_package = Package.objects.filter(operator=Operator.MCI.value)
        # Update current packages
        for package in all_mci_package:
            search_mci_package(package, response_desc)
        # Add new packages
        for res in response_desc:
            obj, created = Package.objects.get_or_create(
                package_type=int(res['Package_Type']),
                operator=Operator.MCI.value,
                defaults={'name': res['Package_Desc'], 'description': res['Package_Desc'],
                          'amount': int(res['Package_Cost'] or 999), 'system': int(res['Systems'] or 100)},
            )
        else:
            print("************* Error in updating MCCI packages!  ***********")


class ChargeCallSaleView(BaseAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def post(request):
        # if expired():
        #     return Response()
        broker = request.user.broker
        operator = request.data.get('operator')
        amount = request.data.get('amount')
        tell_num = request.data.get('tell_num')
        tell_charger = request.data.get('tell_charger')
        charge_type = request.data.get('charge_type')

        data = {"message": '', "message_fa": "پارامترهای ارسالی نادرست است", "code": codes.invalid_parameter}
        if not operator or not isinstance(operator, int) or operator not in [Operator.MCI.value, Operator.MTN.value,
                                                                             Operator.RIGHTEL.value]:
            data["message"] = "'operator' is not provided or valid."
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        if not amount:
            data["message"] = "'amount' is not provided."
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        if not tell_num:
            data["message"] = "'tell_num' is not provided."
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        if not tell_charger:
            data["message"] = "'tell_charger' is not provided."
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        if not charge_type:
            data["message"] = "'charge_type' is not provided."
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        if operator == Operator.MTN.value and charge_type == chargecode.MOSTAGHIM.value:
            charge_type = chargecode.MTN_DIRECT.value
        elif operator == Operator.MTN.value and charge_type == chargecode.FOGHOLAADE.value:
            charge_type = chargecode.MTN_SPECIAL.value
        elif operator == Operator.RIGHTEL.value and charge_type == chargecode.MOSTAGHIM.value:
            charge_type = chargecode.RIGHTEL_DIRECT.value
        elif operator == Operator.RIGHTEL.value and charge_type == chargecode.FOGHOLAADE.value:
            charge_type = chargecode.RIGHTEL_SPECIAL.value
        elif operator == Operator.MCI.value:
            pass
        else:
            print('here')
            data["message"] = "'charge_type' is not valid."
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        try:
            operator_access = broker.operatoraccess_set.get(operator=operator)
            if (not operator_access.active) or (not operator_access.can_sell(top_up=True)):
                data = {
                    "message": "Broker does not have access for this action",
                    "message_fa": "خطا: کاربر دسترسی لازم برای این عملیات را ندارد.",
                    "code": codes.invalid_access,
                }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            try:
                operator_access.banned_charge_types.get(charge_type=charge_type)
                data = {
                    "message": "Broker does not have access to use this type of charge",
                    "message_fa": "خطا: کاربر دسترسی لازم برای استفاده از این نوع شارژ راندارد.",
                    "code": codes.invalid_charge_access,
                }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            except ChargeType.DoesNotExist:
                pass
            top_up = TopUp.create(
                operator=operator,
                amount=amount,
                broker=broker,
                tell_num=tell_num,
                tell_charger=tell_charger,
                charge_type=charge_type,
            )
        except OperatorAccess.DoesNotExist as e:
            data = {
                "message": "Broker does not have access for this action",
                "message_fa": "خطا: کاربر دسترسی لازم برای این عملیات را ندارد.",
                "code": codes.invalid_access,
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            data = {
                "error_dict": str(e.message_dict),
                "message": str(e.messages[0]),
                "message_fa": "خطا: پارامترهای غیر معتبر",
                "code": codes.invalid_parameter,
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        if operator_access.get_credit(top_up=True) < top_up.amount:
            top_up.state = RecordState.INITIAL_ERROR.value
            top_up.save()
            data = {
                "message": "Brokers balance is insufficient",
                "message_fa": "اعتبار کارگزار کافی نیست.",
                "code": codes.insufficient_balance,
            }
            return Response(data, status=status.HTTP_200_OK)

        if operator == Operator.MCI.value:
            call_response_type, call_response_description = MCI().charge_call_sale(
                top_up.tell_num,
                top_up.tell_charger,
                top_up.amount,
                top_up.charge_type,
            )
        elif operator in [Operator.MTN.value, Operator.RIGHTEL.value]:
            top_up.before_call(operator=operator)
            call_response_type, call_response_description = EWays().call_sale(int(top_up.uid))

        success = top_up.after_call(call_response_type, call_response_description)
        if success:
            data = {
                "message": "Request successfully submitted",
                "message_fa": "درخواست با موفقیت ثبت شد",
                "code": codes.successful,
                "provider_id": top_up.provider_id
            }
            return Response(data, status=status.HTTP_200_OK)
        elif int(call_response_type) == 19:
            data = {
                "message": "Failed to execute request",
                "message_fa": top_up.exe_response_description,
                "code": codes.invalid_parameter,
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        else:
            data = {
                "message": "Failed to submit request",
                "message_fa": top_up.call_response_description,
                "code": top_up.call_response_type,
            }
            return Response(data, status=status.HTTP_200_OK)

        # if operator in [Operator.MTN.value, Operator.RIGHTEL.value]:
        #     top_up.before_call(operator=operator)
        #     call_response_type, call_response_description = EWays().call_sale(int(top_up.uid))
        #     success = top_up.after_call(call_response_type, call_response_description)
        #     if success:
        #         data = {
        #             "message": "Request successfully submitted",
        #             "message_fa": "درخواست با موفقیت ثبت شد",
        #             "code": codes.successful,
        #             "provider_id": top_up.provider_id
        #         }
        #         return Response(data, status=status.HTTP_200_OK)
        #     else:
        #         data = {
        #             "message": "Failed to execute request",
        #             "message_fa": top_up.exe_response_description,
        #             "code": codes.invalid_parameter,
        #         }
        #         return Response(data, status=status.HTTP_200_OK)


class ChargeExeSaleView(BaseAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def post(request):
        # if expired():
        #     return Response()
        try:
            broker = request.user.broker
            provider_id = request.data.get('provider_id')
            bank_code = request.data.get('bank_code')
            card_number = request.data.get('card_number')
            card_type = request.data.get('card_type')

            data = {"message": '', "message_fa": "پارامترهای ارسالی نادرست است", "code": codes.invalid_parameter}
            if not provider_id:
                data["message"] = "'charge_type' is not provided."
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            top_up = TopUp.objects.get(provider_id=provider_id, broker=broker)
            if top_up.state == RecordState.CALLED.value:
                try:
                    top_up.before_execute(
                        bank_code=bank_code,
                        card_number=card_number,
                        card_type=card_type
                    )
                except ValidationError as e:
                    data = {
                        "message": str(e.messages[0]),
                        "message_fa": "خطا: پارامترهای غیر معتبر",
                        "code": codes.invalid_parameter,
                    }
                    return Response(data, status=status.HTTP_400_BAD_REQUEST)
            else:
                data = {
                    "message": "Invalid 'provider_id'",
                    "message_fa": "خطا: پارامتر provider_id غیر معتبر",
                    "code": codes.invalid_parameter,
                }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            data = {
                "message": "Invalid parameters",
                "message_fa": "خطا: پارامترهای غیر معتبر",
                "code": codes.invalid_parameter,
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        operator = top_up.operator

        try:
            operator_access = broker.operatoraccess_set.get(operator=operator)
            if (not operator_access.active) or (not operator_access.can_sell(top_up=True)):
                data = {
                    "message": "Broker does not have access for this action",
                    "message_fa": "خطا: کاربر دسترسی لازم برای این عملیات را ندارد.",
                    "code": codes.invalid_access,
                }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
        except OperatorAccess.DoesNotExist as e:
            data = {
                "message": "Broker does not have access for this action",
                "message_fa": "خطا: کاربر دسترسی لازم برای این عملیات را ندارد.",
                "code": codes.invalid_access,
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        if operator_access.get_credit(top_up=True) < top_up.amount:
            data = {
                "message": "Brokers balance is insufficient",
                "message_fa": "اعتبار کارگزار کافی نیست.",
                "code": codes.insufficient_balance,
            }
            return Response(data, status=status.HTTP_200_OK)
        exe_response_type = -1
        exe_response_description = ''
        if top_up.operator == Operator.MCI.value:
            exe_response_type, exe_response_description = MCI().charge_exe_sale(
                provider_id=top_up.provider_id,
                bank_code=top_up.bank_code,
                card_no=top_up.card_number,
                card_type=top_up.card_type
            )
        elif top_up.operator in [Operator.MTN.value, Operator.RIGHTEL.value]:
            exe_response_type, exe_response_description = EWays().exe_sale(top_up.provider_id, int(top_up.charge_type),
                                                                           int(top_up.amount), int(top_up.tell_charger))
        success = top_up.after_execute(exe_response_type, exe_response_description)
        if success:
            # modify change chargin method
            # broker.charge_for_mcci_transaction(top_up.amount)
            operator_access.charge(amount=top_up.amount, top_up=True, record=top_up)
            data = {
                "message": "Request successfully executed",
                "message_fa": "درخواست با موفقیت اجرا شد",
                "code": codes.successful,
            }
            return Response(data, status=status.HTTP_200_OK)
        elif int(exe_response_type) == 19:
            data = {
                "message": "Failed to execute request",
                "message_fa": top_up.exe_response_description,
                "code": codes.invalid_parameter,
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        else:
            data = {
                "message": "Failed to execute request",
                "message_fa": top_up.exe_response_description,
                "code": top_up.exe_response_type,
            }
            return Response(data, status=status.HTTP_200_OK)

        # if top_up.operator in [Operator.MTN.value, Operator.RIGHTEL.value]:
        #     exe_response_type, exe_response_description = EWays().exe_sale(top_up.provider_id, int(top_up.charge_type),
        #                                                                    int(top_up.amount), int(top_up.tell_charger))
        #     success = top_up.after_execute(exe_response_type, exe_response_description)
        #     if success:
        #         operator_access.charge(amount=top_up.amount, top_up=True, record=top_up)
        #         data = {
        #             "message": "Request successfully executed",
        #             "message_fa": "درخواست با موفقیت اجرا شد",
        #             "code": codes.successful,
        #         }
        #         return Response(data, status=status.HTTP_200_OK)
        #     else:
        #         data = {
        #             "message": "Failed to execute request",
        #             "message_fa": top_up.exe_response_description,
        #             "code": top_up.exe_response_type,
        #         }
        #         return Response(data, status=status.HTTP_200_OK)


class PackageCallSaleView(BaseAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def post(request):
        # if expired():
        #     return Response()
        broker = request.user.broker
        operator = request.data.get('operator')
        tell_num = request.data.get('tell_num')
        tell_charger = request.data.get('tell_charger')
        package_type = request.data.get('package_type')
        package_amount = request.data.get("amount")

        data = {"message": '', "message_fa": "پارامترهای ارسالی نادرست است", "code": codes.invalid_parameter}
        if not operator or not isinstance(operator, int) or operator not in [Operator.MCI.value, Operator.MTN.value,
                                                                             Operator.RIGHTEL.value]:
            data["message"] = "'operator' is not provided."
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        if not tell_num:
            data["message"] = "'tell_num' is not provided."
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        if not tell_charger:
            data["message"] = "'tell_charger' is not provided."
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        if not package_type:
            data["message"] = "'package_type' is not provided."
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        if not package_amount:
            data["message"] = "'package_amount' is not provided."
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        try:
            package = Package.objects.get(package_type=package_type, operator=operator)
            operator_access = broker.operatoraccess_set.get(operator=operator)
            if (not operator_access.active) or (not operator_access.can_sell(top_up=False)):
                data = {
                    "message": "Broker does not have access for this action",
                    "message_fa": "خطا: کاربر دسترسی لازم برای این عملیات را ندارد.",
                    "code": codes.invalid_access,
                }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            try:
                operator_access.banned_packages.get(package_type=package.package_type)
                data = {
                    "message": "Broker does not have access to activate this package",
                    "message_fa": "خطا: کاربر دسترسی لازم برای فعال سازی این بسته راندارد.",
                    "code": codes.invalid_package_access,
                }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            except Package.DoesNotExist:
                pass

            if int(package_amount) != package.PackageCostWithVat:
                data = {
                    "message": "Failed to execute request",
                    "message_fa": ResponseTypes.INVALIPACKAGEAMOUNT.farsi(ResponseTypes.INVALIPACKAGEAMOUNT.value),
                    "code": ResponseTypes.INVALIPACKAGEAMOUNT.value,
                }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

            package_amount = package.amount

            package_record = PackageRecord.create(
                broker=broker,
                operator=operator,
                tell_num=tell_num,
                tell_charger=tell_charger,
                package=package,
                amount=package_amount
            )
        except ValidationError as e:
            data = {
                "message": str(e.messages[0]),
                "message_fa": "خطا: پارامترهای غیر معتبر",
                "code": codes.invalid_parameter,
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        except Package.DoesNotExist as e:
            data = {
                "message": "package does not exist with this package_type for this operator",
                "message_fa": "خطا: پکیج با این مشخصات یافت نشد",
                "code": codes.invalid_parameter,
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        except OperatorAccess.DoesNotExist as e:
            data = {
                "message": "Broker does not have access for this action",
                "message_fa": "خطا: کاربر دسترسی لازم برای این عملیات را ندارد.",
                "code": codes.invalid_access,
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        if operator_access.get_credit(top_up=False) < package_record.amount:
            package_record.state = RecordState.INITIAL_ERROR.value
            package_record.save()
            data = {
                "message": "Brokers balance is insufficient",
                "message_fa": "اعتبار کارگزار کافی نیست.",
                "code": codes.insufficient_balance,
            }
            return Response(data, status=status.HTTP_200_OK)
        call_response_type = -1
        call_response_description = ''
        if operator == Operator.MCI.value:
            call_response_type, call_response_description = MCI().package_call_sale(
                package_record.tell_num,
                package_record.tell_charger,
                package_record.amount,
                package_record.package.package_type,
            )
        elif operator in [Operator.MTN.value, Operator.RIGHTEL.value]:
            package_record.before_call(operator=operator)
            call_response_type, call_response_description = EWays().call_sale(int(package_record.uid))

        success = package_record.after_call(call_response_type, call_response_description)
        if success:
            data = {
                "message": "Request successfully submitted",
                "message_fa": "درخواست با موفقیت ثبت شد",
                "code": codes.successful,
                "provider_id": package_record.provider_id
            }
            return Response(data, status=status.HTTP_200_OK)
        elif int(call_response_type) == 19:
            data = {
                "message": "Failed to execute request",
                "message_fa": package_record.exe_response_description,
                "code": codes.invalid_parameter,
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            data = {
                "message": "Failed to submit request",
                "message_fa": package_record.call_response_description,
                "code": package_record.call_response_type,
            }
            return Response(data, status=status.HTTP_200_OK)


class PackageExeSaleView(BaseAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def post(request):
        # if expired():
        #     return Response()
        try:
            broker = request.user.broker
            provider_id = request.data.get('provider_id')
            bank_code = request.data.get('bank_code')
            card_number = request.data.get('card_number')
            card_type = request.data.get('card_type')
            package_record = PackageRecord.objects.get(provider_id=provider_id, broker=broker)
            if package_record.state == RecordState.CALLED.value:
                package_record.before_execute(
                    bank_code=bank_code,
                    card_number=card_number,
                    card_type=card_type
                )
            else:
                data = {
                    "message": "Invalid provider_id: could not find a record with valid call sale",
                    "message_fa": "خطا: پارامتر provider_id غیر معتبر",
                    "code": codes.invalid_parameter,
                }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            operator = package_record.operator
            operator_access = broker.operatoraccess_set.get(operator=operator)
            if (not operator_access.active) or (not operator_access.can_sell(top_up=False)):
                data = {
                    "message": "Broker does not have access for this action",
                    "message_fa": "خطا: کاربر دسترسی لازم برای این عملیات را ندارد.",
                    "code": codes.invalid_access,
                }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
        except OperatorAccess.DoesNotExist as e:
            data = {
                "message": "Broker does not have access for this action",
                "message_fa": "خطا: کاربر دسترسی لازم برای این عملیات را ندارد.",
                "code": codes.invalid_access,
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            data = {
                "message": str(e.messages[0]),
                "message_fa": "خطا: پارامترهای غیر معتبر",
                "code": codes.invalid_parameter,
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        except PackageRecord.DoesNotExist:
            data = {
                "message": "package_record does not exist with this provider_id",
                "message_fa": "خطا: درخواست پکیج با این مشخصات یافت نشد",
                "code": codes.invalid_parameter,
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        if operator_access.get_credit(top_up=False) < package_record.package.amount:
            data = {
                "message": "Brokers balance is insufficient",
                "message_fa": "اعتبار کارگزار کافی نیست.",
                "code": codes.insufficient_balance,
            }
            return Response(data, status=status.HTTP_200_OK)
        exe_response_type = -1
        exe_response_description = ''
        if package_record.amount != package_record.package.amount:
            data = {
                "message": "Failed to execute request",
                "message_fa": ResponseTypes.INVALIPACKAGEAMOUNT.farsi(ResponseTypes.INVALIPACKAGEAMOUNT.value),
                "code": ResponseTypes.INVALIPACKAGEAMOUNT.value,
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        if operator == Operator.MCI.value:
            exe_response_type, exe_response_description = MCI().package_exe_sale(
                provider_id=package_record.provider_id,
                bank_code=package_record.bank_code,
                card_no=package_record.card_number,
                card_type=package_record.card_type
            )
        elif operator == Operator.MTN.value:
            exe_response_type, exe_response_description = EWays().exe_sale(
                package_record.provider_id, '33', int(package_record.package.PackageCostWithVat), package_record.tell_charger, package_record.package.package_type)
        elif operator == Operator.RIGHTEL.value:
            exe_response_type, exe_response_description = EWays().exe_sale(
                package_record.provider_id, '62', int(package_record.package.PackageCostWithVat), package_record.tell_charger, package_record.package.package_type)
        success = package_record.after_execute(exe_response_type, exe_response_description)
        if success:
            operator_access.charge(amount=package_record.amount, top_up=False, record=package_record)
            data = {
                "message": "Request successfully executed",
                "message_fa": "درخواست با موفقیت اجرا شد",
                "code": codes.successful,
            }
            return Response(data, status=status.HTTP_200_OK)
        elif int(exe_response_type) == 19:
            data = {
                "message": "Failed to execute request",
                "message_fa": package_record.exe_response_description,
                "code": codes.invalid_parameter,
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            data = {
                "message": "Failed to execute request",
                "message_fa": package_record.exe_response_description,
                "code": package_record.exe_response_type,
            }
            return Response(data, status=status.HTTP_200_OK)



class TransactionStatusInquiry(BaseAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def post(request):
        if expired():
            return Response()
        try:
            broker = request.user.broker
            provider_id = request.data.get('provider_id')
            tell_num = request.data.get('TelNum')
            operator = int(request.data.get('operator'))
            transaction_type = request.data.get('transaction_type')
            data = {"message": '', "message_fa": "پارامترهای ارسالی نادرست است", "code": codes.invalid_parameter}
            if not provider_id:
                data["message"] = "'provider_id' is not provided."
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            if not tell_num:
                data["message"] = "'tell_num' is not provided."
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            if not transaction_type or transaction_type not in [1, 2]:
                data["message"] = "'transaction_type' is not provided or valid."
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

            if not operator or not isinstance(operator, int) or operator not in [Operator.MCI.value, Operator.MTN.value,
                                                                                 Operator.RIGHTEL.value]:
                data["message"] = "'operator' is not provided or valid."
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            operator_access = broker.operatoraccess_set.get(operator=operator)
            if not operator_access.active:
                data = {
                    "message": "Broker does not have access for this action",
                    "message_fa": "خطا: کاربر دسترسی لازم برای این عملیات را ندارد.",
                    "code": codes.invalid_access,
                }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

            if transaction_type == 1:
                log_record = TopUp.objects.get(provider_id=provider_id, tell_num=tell_num,operator=operator)
                # if operator in [Operator.MCI.value,Operator.MTN.value, Operator.RIGHTEL.value]:
                # res = MCI().behsa_charge_status(provider_id=provider_id, TelNum=tell_num, Bank=TopUp.bank_code)
                if log_record.state == RecordState.EXECUTED.value:
                    data = {
                        "message": "Request successfully executed",
                        "message_fa": "درخواست با موفقیت اجرا شد",
                        "code": codes.successful,
                        "transaction_status": 1,
                        "transaction_type": log_record.charge_type,
                        "execution_time": "" if log_record.execution_time is None else log_record.execution_time.strftime(
                            "%Y/%m/%d %H:%M:%S"),
                        "exe_response_code": "" if log_record.exe_response_type is None else log_record.exe_response_type,
                        "exe_response_description": "" if log_record.exe_response_description is None else log_record.exe_response_description
                    }
                    return Response(data, status=status.HTTP_200_OK)
                elif log_record.state == RecordState.EXE_REQ.value:
                    data = {
                        "message": "Request successfully executed",
                        "message_fa": "درخواست با موفقیت اجرا شد",
                        "code": codes.successful,
                        "transaction_status": -1,
                        "transaction_type": log_record.charge_type,
                        "execution_time": "" if log_record.execution_time is None else log_record.execution_time.strftime(
                            "%Y/%m/%d %H:%M:%S"),
                        "exe_response_code": "" if log_record.exe_response_type is None else log_record.exe_response_type,
                        "exe_response_description": "" if log_record.exe_response_description is None else log_record.exe_response_description
                    }
                    return Response(data, status=status.HTTP_200_OK)
                else:
                    data = {
                        "message": "Request successfully executed",
                        "message_fa": "درخواست با موفقیت اجرا شد",
                        "code": codes.successful,
                        "transaction_status": -1,
                        "transaction_type": log_record.charge_type,
                        "execution_time": "" if log_record.execution_time is None else log_record.execution_time.strftime(
                            "%Y/%m/%d %H:%M:%S"),
                        "exe_response_code": "" if log_record.exe_response_type is None else log_record.exe_response_type,
                        "exe_response_description": "" if log_record.exe_response_description is None else log_record.exe_response_description
                    }
                    return Response(data, status=status.HTTP_200_OK)

                # should be modified with eways services
                # if operator in [Operator.MTN.value, Operator.RIGHTEL.value]:
                #     pass

            elif transaction_type == 2:
                log_record = PackageRecord.objects.get(provider_id=provider_id, tell_num=tell_num,operator=operator)
                # if operator in [Operator.MCI.value,Operator.MTN.value, Operator.RIGHTEL.value]:
                # res = MCI().behsa_package_status(provider_id=provider_id, TelNum=tell_num, Bank=TopUp.bank_code)
                if log_record.state == RecordState.EXECUTED.value:
                    data = {
                        "message": "Request successfully executed",
                        "message_fa": "درخواست با موفقیت اجرا شد",
                        "code": codes.successful,
                        "transaction_status": 1,
                        "transaction_type": log_record.package.package_type,
                        "execution_time": "" if log_record.execution_time is None else log_record.execution_time.strftime(
                            "%Y/%m/%d %H:%M:%S"),
                        "exe_response_code": "" if log_record.exe_response_type is None else log_record.exe_response_type,
                        "exe_response_description": "" if log_record.exe_response_description is None else log_record.exe_response_description
                    }
                    return Response(data, status=status.HTTP_200_OK)
                elif log_record.state == RecordState.EXE_REQ.value:
                    data = {
                        "message": "Request successfully executed",
                        "message_fa": "درخواست با موفقیت اجرا شد",
                        "code": codes.successful,
                        "transaction_status": -1,
                        "transaction_type": log_record.charge_type,
                        "execution_time": "" if log_record.execution_time is None else log_record.execution_time.strftime(
                            "%Y/%m/%d %H:%M:%S"),
                        "exe_response_code": "" if log_record.exe_response_type is None else log_record.exe_response_type,
                        "exe_response_description": "" if log_record.exe_response_description is None else log_record.exe_response_description
                    }
                    return Response(data, status=status.HTTP_200_OK)
                else:
                    data = {
                        "message": "Request successfully executed",
                        "message_fa": "درخواست با موفقیت اجرا شد",
                        "code": codes.successful,
                        "transaction_status": -1,
                        "transaction_type": log_record.package.package_type,
                        "execution_time": "" if log_record.execution_time is None else log_record.execution_time.strftime(
                            "%Y/%m/%d %H:%M:%S"),
                        "exe_response_code": "" if log_record.exe_response_type is None else log_record.exe_response_type,
                        "exe_response_description": "" if log_record.exe_response_description is None else log_record.exe_response_description
                    }
                    return Response(data, status=status.HTTP_200_OK)

                # should be modified with eways services
                # if operator in [Operator.MTN.value, Operator.RIGHTEL.value]:
                #     pass
        except OperatorAccess.DoesNotExist as e:
            data = {
                "message": "Broker does not have access for this action",
                "message_fa": "خطا: کاربر دسترسی لازم برای این عملیات را ندارد.",
                "code": codes.invalid_access,
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            data = {
                "message": str(e.messages[0]),
                "message_fa": "خطا: پارامترهای غیر معتبر",
                "code": codes.invalid_parameter,
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            data = {
                "message": str(e),
                "message_fa": "پارامترهای ارسالی نادرست است.",
                "code": codes.invalid_parameter,
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)


class BrokerCreditView(BaseAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def get(request):
        try:
            broker = request.user.broker
            acceses = broker.operatoraccess_set.filter(active=True)
            serialized_data = OperatorAccessSerializer(acceses,many=True).data
            print(serialized_data)
        except OperatorAccess.DoesNotExist as e:
            data = {
                "message": "Broker does not have access for this action",
                "message_fa": "خطا: کاربر دسترسی لازم برای این عملیات را ندارد.",
                "code": codes.invalid_access,
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            data = {
                "message": "Invalid Broker",
                "message_fa": "خطا: کارگزار نامعتبر است.",
                "code": codes.invalid_parameter,
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        if not broker.active:
            data = {
                "message": "Brokers is not active",
                "message_fa": "کارگذار غیرفعال است.",
                "code": codes.inactive_broker,
            }
            return Response(data, status=status.HTTP_200_OK)

        # general_credit = 0
        # topup_credit = 0
        # package_credit = 0
        # if operator_access.general_credit_access:
        #     general_credit = operator_access.get_credit(top_up=True)
        # else:
        #     topup_credit = operator_access.get_credit(top_up=True)
        #     package_credit = operator_access.get_credit(top_up=False)

        data = {
            "message": "Request successfully executed",
            "message_fa": "درخواست با موفقیت اجرا شد",
            "code": codes.successful,
            "credit" : serialized_data
            # "general_credit": general_credit,
            # "topup_credit": topup_credit,
            # "package_credit": package_credit
        }
        return Response(data, status=status.HTTP_200_OK)


class RaceTest(BaseAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def post(request):
        with transaction.atomic():
            try:
                broker = Broker.objects.get(user=request.user)
                operator_access = broker.operatoraccess_set.get(operator=Operator.MCI.value)
                operator_access.charge(1, True)
                data = {
                    "message": "Request successfully executed",
                    "message_fa": "درخواست با موفقیت اجرا شد",
                    "code": codes.successful,
                }
                return Response(data, status=status.HTTP_200_OK)
            except OperatorAccess.DoesNotExist as e:
                data = {
                    "message": "Broker does not have access for this action",
                    "message_fa": "خطا: کاربر دسترسی لازم برای این عملیات را ندارد.",
                    "code": codes.invalid_access,
                }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                data = {
                    "message": "Broker does not have access for this action",
                    "message_fa": "خطا: کاربر دسترسی لازم برای این عملیات را ندارد.",
                    "code": codes.invalid_access,
                }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)


class ActivePackages(BaseAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def get(request):
        operator = request.GET.get('operator', 1)
        data = {"code": codes.invalid_parameter, "message_fa": "خطا: ارسال نشدن همه پارامترها"}
        if not operator or not isinstance(operator, int) or operator not in [Operator.MCI.value, Operator.MTN.value,
                                                                             Operator.RIGHTEL.value]:
            data["message"] = "'operator' is not provided or not valid."
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        try:
            broker = request.user.broker
            operator_access = broker.operatoraccess_set.get(operator=operator)
            if not operator_access.active:
                data = {
                    "message": "Broker does not have access for this action",
                    "message_fa": "خطا: کاربر دسترسی لازم برای این عملیات را ندارد.",
                    "code": codes.invalid_access,
                }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            banned_package = operator_access.banned_packages.all().values('id')
            serialized_data = PackageSerializer(Package.objects.filter(active=True).exclude(id__in=banned_package),
                                                many=True).data
            data = {
                "message": "Request successfully executed",
                "message_fa": "درخواست با موفقیت اجرا شد",
                "code": codes.successful,
                "packages": serialized_data
            }
            return Response(data, status=status.HTTP_200_OK)
        except OperatorAccess.DoesNotExist as e:
            data = {
                "message": "Broker does not have access for this action",
                "message_fa": "خطا: کاربر دسترسی لازم برای این عملیات را ندارد.",
                "code": codes.invalid_access,
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            data = {
                "message": "Broker does not have access for this action",
                "message_fa": "خطا: کاربر دسترسی لازم برای این عملیات را ندارد.",
                "code": codes.invalid_access,
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)


class TestApi58(BaseAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def post(request):
        if expired():
            return Response()
        try:
            broker = request.user.broker
            provider_id = request.data.get('provider_id')
            tell_num = request.data.get('TelNum')
            operator = int(request.data.get('operator'))
            transaction_type = request.data.get('transaction_type')
            data = {"message": '', "message_fa": "پارامترهای ارسالی نادرست است", "code": codes.invalid_parameter}
            if not provider_id:
                data["message"] = "'provider_id' is not provided."
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            if not tell_num:
                data["message"] = "'tell_num' is not provided."
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            if not transaction_type or transaction_type not in [1, 2]:
                data["message"] = "'transaction_type' is not provided or valid."
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

            if not operator or not isinstance(operator, int) or operator not in [Operator.MCI.value, Operator.MTN.value,
                                                                                 Operator.RIGHTEL.value]:
                data["message"] = "'operator' is not provided or valid."
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            operator_access = broker.operatoraccess_set.get(operator=operator)
            if not operator_access.active:
                data = {
                    "message": "Broker does not have access for this action",
                    "message_fa": "خطا: کاربر دسترسی لازم برای این عملیات را ندارد.",
                    "code": codes.invalid_access,
                }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)







            log_record = PackageRecord.objects.get(provider_id=provider_id, tell_num=tell_num, operator=operator)

            data = {
                "message": "Delete It",
                "message_fa": str(MCI().behsa_package_status(provider_id=provider_id, TelNum=tell_num, Bank=log_record.bank_code)),
                "code": codes.service_error,
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

            if transaction_type == 1:
                # log_record = TopUp.objects.get(provider_id=provider_id, tell_num=tell_num,
                #                                operator=operator)
                log_record = TopUp.objects.get(tell_num=tell_num, operator=operator)##################delete this
                print('here')
                if operator == Operator.MCI.value:
                    try:
                        res_type, res_desc, res_status, res_date, res_time = MCI().behsa_charge_status(provider_id=provider_id, TelNum=tell_num, Bank=TopUp.bank_code)
                    except:
                        data = {
                            "message": "Service is not available now, please try again later",
                            "message_fa": "خطا: به شرح خطای اعلامی رجوع گردد",
                            "code": codes.service_error,
                        }
                        return Response(data, status=status.HTTP_400_BAD_REQUEST)
                    if res_type == 0:
                      if res_status == 1:
                          pass
                      elif res_status == 0:
                          pass
                      elif res_status == -1:
                          pass
                      else:
                          data = {
                              "message": res_desc,
                              "message_fa": res_status,
                              "code": codes.service_error,
                          }
                          return Response(data, status=status.HTTP_400_BAD_REQUEST)

                    else:
                        data = {
                            "message": res_desc,
                            "message_fa": "خطا: به شرح خطای اعلامی رجوع گردد",
                            "code": codes.service_error,
                        }
                        return Response(data, status=status.HTTP_400_BAD_REQUEST)





                    if log_record.state == RecordState.EXECUTED.value:
                        data = {
                            "message": "Request successfully executed",
                            "message_fa": "درخواست با موفقیت اجرا شد",
                            "code": codes.successful,
                            "transaction_status": 1,
                            "transaction_type": log_record.charge_type,
                            "execution_time": "" if log_record.execution_time is None else log_record.execution_time.strftime(
                                "%Y/%m/%d %H:%M:%S"),
                            "exe_response_code": "" if log_record.exe_response_type is None else log_record.exe_response_type,
                            "exe_response_description": "" if log_record.exe_response_description is None else log_record.exe_response_description
                        }
                        return Response(data, status=status.HTTP_200_OK)
                    elif log_record.state == RecordState.EXE_REQ.value:
                        data = {
                            "message": "Request successfully executed",
                            "message_fa": "درخواست با موفقیت اجرا شد",
                            "code": codes.successful,
                            "transaction_status": 0,
                            "transaction_type": log_record.charge_type,
                            "execution_time": "" if log_record.execution_time is None else log_record.execution_time.strftime(
                                "%Y/%m/%d %H:%M:%S"),
                            "exe_response_code": "" if log_record.exe_response_type is None else log_record.exe_response_type,
                            "exe_response_description": "" if log_record.exe_response_description is None else log_record.exe_response_description
                        }
                        return Response(data, status=status.HTTP_200_OK)
                    else:
                        data = {
                            "message": "Request successfully executed",
                            "message_fa": "درخواست با موفقیت اجرا شد",
                            "code": codes.successful,
                            "transaction_status": -1,
                            "transaction_type": log_record.charge_type,
                            "execution_time": "" if log_record.execution_time is None else log_record.execution_time.strftime(
                                "%Y/%m/%d %H:%M:%S"),
                            "exe_response_code": "" if log_record.exe_response_type is None else log_record.exe_response_type,
                            "exe_response_description": "" if log_record.exe_response_description is None else log_record.exe_response_description
                        }
                        return Response(data, status=status.HTTP_200_OK)

                # should be modified with eways services
                if operator in [Operator.MTN.value, Operator.RIGHTEL.value]:
                    pass

            elif transaction_type == 2:
                log_record = PackageRecord.objects.get(provider_id=provider_id, tell_num=tell_num,
                                                       operator=Operator.MCI.value)
                if operator == Operator.MCI.value:
                    res = MCI().behsa_package_status(provider_id=provider_id, TelNum=tell_num, Bank=TopUp.bank_code)
                    if log_record.state == RecordState.EXECUTED.value:
                        data = {
                            "message": "Request successfully executed",
                            "message_fa": "درخواست با موفقیت اجرا شد",
                            "code": codes.successful,
                            "transaction_status": 1,
                            "transaction_type": log_record.package.package_type,
                            "execution_time": "" if log_record.execution_time is None else log_record.execution_time.strftime(
                                "%Y/%m/%d %H:%M:%S"),
                            "exe_response_code": "" if log_record.exe_response_type is None else log_record.exe_response_type,
                            "exe_response_description": "" if log_record.exe_response_description is None else log_record.exe_response_description
                        }
                        return Response(data, status=status.HTTP_200_OK)
                    elif log_record.state == RecordState.EXE_REQ.value:
                        data = {
                            "message": "Request successfully executed",
                            "message_fa": "درخواست با موفقیت اجرا شد",
                            "code": codes.successful,
                            "transaction_status": 0,
                            "transaction_type": log_record.charge_type,
                            "execution_time": "" if log_record.execution_time is None else log_record.execution_time.strftime(
                                "%Y/%m/%d %H:%M:%S"),
                            "exe_response_code": "" if log_record.exe_response_type is None else log_record.exe_response_type,
                            "exe_response_description": "" if log_record.exe_response_description is None else log_record.exe_response_description
                        }
                        return Response(data, status=status.HTTP_200_OK)
                    else:
                        data = {
                            "message": "Request successfully executed",
                            "message_fa": "درخواست با موفقیت اجرا شد",
                            "code": codes.successful,
                            "transaction_status": -1,
                            "transaction_type": log_record.package.package_type,
                            "execution_time": "" if log_record.execution_time is None else log_record.execution_time.strftime(
                                "%Y/%m/%d %H:%M:%S"),
                            "exe_response_code": "" if log_record.exe_response_type is None else log_record.exe_response_type,
                            "exe_response_description": "" if log_record.exe_response_description is None else log_record.exe_response_description
                        }
                        return Response(data, status=status.HTTP_200_OK)

                # should be modified with eways services
                if operator in [Operator.MTN.value, Operator.RIGHTEL.value]:
                    pass

        except OperatorAccess.DoesNotExist as e:
            data = {
                "message": "Broker does not have access for this action",
                "message_fa": "خطا: کاربر دسترسی لازم برای این عملیات را ندارد.",
                "code": codes.invalid_access,
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            data = {
                "message": str(e.messages[0]),
                "message_fa": "خطا: پارامترهای غیر معتبر",
                "code": codes.invalid_parameter,
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            data = {
                "message": str(e),
                "message_fa": "پارامترهای ارسالی نادرست است.",
                "code": codes.invalid_parameter,
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)


    # @staticmethod
    # def get(request):
    #     try:
    #         broker = Broker.objects.get(user=request.user)
    #         param1 = request.data.get('param1')
    #         param2 = request.data.get('param2')
    #         param3 = request.data.get('param3')
    #         param4 = request.data.get('param4')
    #
    #     except Exception as e:
    #         data = {
    #             "message": "Invalid Broker",
    #             "message_fa": "خطا: کارگزار نامعتبر است.",
    #             "code": codes.invalid_parameter,
    #         }
    #         return Response(data, status=status.HTTP_400_BAD_REQUEST)
    #
    #     if not broker.active:
    #         data = {
    #             "message": "Brokers is not active",
    #             "message_fa": "کارگذار غیرفعال است.",
    #             "code": codes.inactive_broker,
    #         }
    #         return Response(data, status=status.HTTP_200_OK)
    #     # print("************ Get Package Query")
    #     # exe_response_type_0, exe_response_description_0 = MCI().behsa_package_query()
    #
    #     # print("************ Get Package Credit")
    #     # exe_response_type_2, exe_response_description_2 = MCI().behsa_package_credit()
    #     #
    #     # print("************ Get Charge Credit")
    #     # exe_response_type_1, exe_response_description_1 = MCI().behsa_charge_credit()
    #
    #     # print("************ Get subscriber Credit")
    #     # exe_response_type_1, exe_response_description_1 = MCI().behsa_subscriber_charge_credit(param1)
    #     # print("************ Get subscriber package")
    #     # exe_response_type_2, exe_response_description_2 = MCI().behsa_subscriber_package_quata(param1)
    #     # print("************ Get subscriber type")
    #     # exe_response_type_3, exe_response_description_3 = MCI().behsa_subscriber_type(param1)
    #     # update_mci_packages()
    #     # result1_state, uuid = EWays().call_sale(param1)
    #     # result2_state,result2 = EWays().exe_sale(param2, '40', amount, param3)
    #     # result = EWays().exe_sale_test(param1,40,5000,int(param2))
    #     # print(1)
    #     # package_record = PackageRecord.objects.get(provider_id=param1)
    #     # # print('package_record.provider_id'+':'+str(package_record.provider_id))
    #     # # print('package_record.package.PackageCostWithVat'+':'+str(package_record.package.PackageCostWithVat))
    #     # # print('package_record.tell_charger'+':'+str(package_record.tell_charger))
    #     # # print('package_record.package.package_type' + ':' + str(package_record.package.package_type))
    #     #
    #     #
    #     # exe_response_type, exe_response_description = EWays().exe_sale(
    #     #     package_record.provider_id, '33', package_record.package.PackageCostWithVat, package_record.tell_charger,
    #     #     package_record.package.package_type)
    #
    #     # EWays().update_packages()
    #
    #
    #     # resp_code , resp_desc = MCI().package_call_sale(
    #     #         param1,
    #     #         param2,
    #     #         param3,
    #     #         param4,
    #     #     )
    #     resp_code , resp_desc = EWays().get_balance();
    #     data = {
    #         "message": "Request successfully executed",
    #         "message_fa": "درخواست با موفقیت اجرا شد",
    #         "code":resp_code,
    #         "desc":resp_desc
    #         # "result": str(exe_response_description),
    #         # "exe_response_type_0": exe_response_type_0,
    #         # "exe_response_description_0": exe_response_description_0,
    #         # "exe_response_type_1": exe_response_type_1,
    #         # "exe_response_description_1": exe_response_description_1,
    #         # "exe_response_type_2": exe_response_type_2,
    #         # "exe_response_description_2": exe_response_description_2,
    #         # "exe_response_type_3": exe_response_type_3,
    #         # "exe_response_description_3": exe_response_description_3,
    #         # "exe_response_type_2": exe_response_type_2,
    #         # "exe_response_description_2": exe_response_description_2
    #     }
    #     return Response(data, status=status.HTTP_200_OK)
