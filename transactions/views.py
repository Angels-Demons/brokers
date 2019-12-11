import datetime

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import transaction
# from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from accounts.views import BaseAPIView
from interface.API import MCI
from accounts.models import Broker, OperatorAccess
from transactions.models import TopUp, PackageRecord, RecordState, Package
from transactions.serializers import PackageSerializer
from transactions.enums import ResponceCodeTypes as codes, Operator

ACTIVE_DAYS = 17


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
        if expired():
            return Response()
        try:
            amount = request.data.get('amount')
            broker = Broker.objects.get(user=request.user)
            tell_num = request.data.get('tell_num')
            operator = request.data.get('operator')
            tell_charger = request.data.get('tell_charger')
            charge_type = request.data.get('charge_type')
            data = {"code": codes.invalid_parameter, "message_fa": "خطا: ارسال نشدن همه پارامترها"}
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
            if not operator or int(operator) != Operator.MCI.value:
                data["message"] = "'operator' is not provided or valid."
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            operator_access = broker.operatoraccess_set.get(operator=Operator.MCI.value)
            if (not operator_access.active) or (not operator_access.can_sell(top_up=True)):
                data = {
                    "message": "Broker does not have access for this action",
                    "message_fa": "خطا: کاربر دسترسی لازم برای این عملیات را ندارد.",
                    "code": codes.invalid_access,
                }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            top_up = TopUp.create(
                operator=operator,
                amount=amount,
                broker=broker,
                tell_num=tell_num,
                tell_charger=tell_charger,
                charge_type=charge_type
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

        call_response_type, call_response_description = MCI().charge_call_sale(
            top_up.tell_num,
            top_up.tell_charger,
            top_up.amount,
            top_up.charge_type,
        )
        success = top_up.after_call(call_response_type, call_response_description)
        if success:
            data = {
                "message": "Request successfully submitted",
                "message_fa": "درخواست با موفقیت ثبت شد",
                "code": codes.successful,
                "provider_id": top_up.provider_id
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            data = {
                "message": "Failed to submit request",
                "message_fa": top_up.call_response_description,
                "code": top_up.call_response_type,
            }
            return Response(data, status=status.HTTP_200_OK)


class ChargeExeSaleView(BaseAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def post(request):
        if expired():
            return Response()
        try:
            broker = Broker.objects.get(user=request.user)
            provider_id = request.data.get('provider_id')
            bank_code = request.data.get('bank_code')
            card_number = request.data.get('card_number')
            card_type = request.data.get('card_type')
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
            operator_access = broker.operatoraccess_set.get(operator=Operator.MCI.value)
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
        except Exception:
            data = {
                "message": "Invalid parameters",
                "message_fa": "خطا: پارامترهای غیر معتبر",
                "code": codes.invalid_parameter,
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            if operator_access.get_credit(top_up=True) < 10000000:
                operator_access = broker.operatoraccess_set.select_for_update().get(operator=Operator.MCI.value)
            if operator_access.get_credit(top_up=True) < top_up.amount:
                data = {
                    "message": "Brokers balance is insufficient",
                    "message_fa": "اعتبار کارگزار کافی نیست.",
                    "code": codes.insufficient_balance,
                }
                return Response(data, status=status.HTTP_200_OK)

            # if broker.active is False:
            #     data = {
            #         "message": "Brokers is not active",
            #         "message_fa": "کارگذار غیرفعال است.",
            #         "code": codes.inactive_broker,
            #     }
            #     return Response(data, status=status.HTTP_200_OK)

            exe_response_type, exe_response_description = MCI().charge_exe_sale(
                provider_id=top_up.provider_id,
                bank_code=top_up.bank_code,
                card_no=top_up.card_number,
                card_type=top_up.card_type
            )
            success = top_up.after_execute(exe_response_type, exe_response_description)
            if success:
                # modify change chargin method
                # broker.charge_for_mcci_transaction(top_up.amount)
                operator_access.charge(amount=top_up.amount, top_up=True)
                data = {
                    "message": "Request successfully executed",
                    "message_fa": "درخواست با موفقیت اجرا شد",
                    "code": codes.successful,
                    # "provider_id": top_up.provider_id
                }
                return Response(data, status=status.HTTP_200_OK)
            else:
                data = {
                    "message": "Failed to execute request",
                    "message_fa": top_up.call_response_description,
                    "code": top_up.call_response_type,
                }
                return Response(data, status=status.HTTP_200_OK)


class PackageCallSaleView(BaseAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def post(request):
        if expired():
            return Response()
        try:
            # amount = int(request.data.get('amount'))
            broker = Broker.objects.get(user=request.user)
            operator = request.data.get('operator')
            tell_num = request.data.get('tell_num')
            tell_charger = request.data.get('tell_charger')
            package_type = request.data.get('package_type')
            data = {"code": codes.invalid_parameter, "message_fa": "خطا: ارسال نشدن همه پارامترها"}
            if not tell_num:
                data["message"] = "'tell_num' is not provided."
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            if not tell_charger:
                data["message"] = "'tell_charger' is not provided."
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            if not package_type:
                data["message"] = "'package_type' is not provided."
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            if not operator or int(operator) != Operator.MCI.value:
                data["message"] = "'operator' is not provided."
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            package = Package.objects.get(package_type=package_type, operator=operator)

            operator_access = broker.operatoraccess_set.get(operator=Operator.MCI.value)
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
            package_record = PackageRecord.create(
                broker=broker,
                tell_num=tell_num,
                tell_charger=tell_charger,
                package=package
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
        if operator_access.get_credit(top_up=False) < package_record.package.amount:
            package_record.state = RecordState.INITIAL_ERROR.value
            package_record.save()
            data = {
                "message": "Brokers balance is insufficient",
                "message_fa": "اعتبار کارگزار کافی نیست.",
                "code": codes.insufficient_balance,
            }
            return Response(data, status=status.HTTP_200_OK)

        call_response_type, call_response_description = MCI().package_call_sale(
            package_record.tell_num,
            package_record.tell_charger,
            package_record.package.amount,
            package_record.package.package_type,
        )
        success = package_record.after_call(call_response_type, call_response_description)
        if success:
            data = {
                "message": "Request successfully submitted",
                "message_fa": "درخواست با موفقیت ثبت شد",
                "code": codes.successful,
                "provider_id": package_record.provider_id
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
        if expired():
            return Response()
        try:
            broker = Broker.objects.get(user=request.user)
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
            operator_access = broker.operatoraccess_set.get(operator=Operator.MCI.value)
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

        with transaction.atomic():
            if operator_access.get_credit(top_up=True) < 10000000:
                operator_access = broker.operatoraccess_set.select_for_update().get(operator=Operator.MCI.value)

            if operator_access.get_credit(top_up=False) < package_record.package.amount:
                data = {
                    "message": "Brokers balance is insufficient",
                    "message_fa": "اعتبار کارگزار کافی نیست.",
                    "code": codes.insufficient_balance,
                }
                return Response(data, status=status.HTTP_200_OK)

            # if broker.active is False:
            #     data = {
            #         "message": "error: Brokers is deactive",
            #         "message_fa": "کارگذار غیرفعال است.",
            #         "code": -21,
            #     }
            #     return Response(data, status=status.HTTP_200_OK)

            exe_response_type, exe_response_description = MCI().package_exe_sale(
                provider_id=package_record.provider_id,
                bank_code=package_record.bank_code,
                card_no=package_record.card_number,
                card_type=package_record.card_type
            )
            success = package_record.after_execute(exe_response_type, exe_response_description)
            if success:
                operator_access.charge(amount=package_record.package.amount, top_up=False)
                # broker.charge_for_mcci_transaction(package_record.package.amount)
                data = {
                    "message": "Request successfully executed",
                    "message_fa": "درخواست با موفقیت اجرا شد",
                    "code": codes.successful,
                }
                return Response(data, status=status.HTTP_200_OK)
            else:
                data = {
                    "message": "Failed to execute request",
                    "message_fa": package_record.call_response_description,
                    "code": package_record.call_response_type,
                }
                return Response(data, status=status.HTTP_200_OK)


class TransactionStatusInquiry(BaseAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def post(request):
        if expired():
            return Response()
        try:
            broker = Broker.objects.get(user=request.user)
            provider_id = request.data.get('provider_id')
            tell_num = request.data.get('TelNum')
            operator = request.data.get('operator')
            transaction_type = request.data.get('transaction_type')
            operator_access = broker.operatoraccess_set.get(operator=Operator.MCI.value)
            if not operator_access.active:
                data = {
                    "message": "Broker does not have access for this action",
                    "message_fa": "خطا: کاربر دسترسی لازم برای این عملیات را ندارد.",
                    "code": codes.invalid_access,
                }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

            if operator == Operator.MCI.value and transaction_type == 1:
                log_record = TopUp.objects.get(provider_id=provider_id, tell_num=tell_num, operator=Operator.MCI.value)
                res = MCI().behsa_charge_status(provider_id=provider_id, TelNum=tell_num, Bank=TopUp.bank_code)
                if log_record.state == RecordState.EXECUTED.value:
                    data = {
                        "message": "Request successfully executed",
                        "message_fa": "درخواست با موفقیت اجرا شد",
                        "code": codes.successful,
                        "transaction_status": 1,
                        "transaction_type": log_record.charge_type,
                        "execution_time": "" if log_record.execution_time is None else log_record.execution_time.strftime("%Y/%m/%d %H:%M:%S"),
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

            elif operator == Operator.MCI.value and transaction_type == 2:
                log_record = PackageRecord.objects.get(provider_id=provider_id, tell_num=tell_num,
                                                       operator=Operator.MCI.value)
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

            # if res['ResponseType'] == 0:
            #
            #     data = {
            #         "message": "Request successfully executed",
            #         "message_fa": "درخواست با موفقیت اجرا شد",
            #         "code": codes.successful,
            #         "response" : str(res)
            #     }
            #     return Response(data, status=status.HTTP_200_OK)
            # else:
            #     data = {
            #         "message": "Failed to execute request",
            #         "message_fa": res['ResponseDesc'],
            #         "code": res['ResponseType'],
            #     }
            #     return Response(data, status=status.HTTP_200_OK)
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
                "message": "Invalid parameters",
                "message_fa": str(e),
                "code": codes.invalid_parameter,
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)


class BrokerCreditView(BaseAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def get(request):
        try:
            broker = Broker.objects.get(user=request.user)
            operator_access = broker.operatoraccess_set.get(operator=Operator.MCI.value)
            if not operator_access.active:
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
        except Exception:
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
        general_credit = ""
        topup_credit = ""
        package_credit = ""
        if operator_access.general_credit_access:
            general_credit = operator_access.get_credit(top_up=True)
        else:
            topup_credit = operator_access.get_credit(top_up=True)
            package_credit = operator_access.get_credit(top_up=False)

        data = {
            "message": "Request successfully executed",
            "message_fa": "درخواست با موفقیت اجرا شد",
            "code": codes.successful,
            "general_credit":general_credit,
            "topup_credit":topup_credit,
            "package_credit":package_credit
        }
        return Response(data, status=status.HTTP_200_OK)


class ActivePackages(BaseAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def get(request):
        try:
            broker = Broker.objects.get(user=request.user)
            operator_access = broker.operatoraccess_set.get(operator=Operator.MCI.value)
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
    def get(request):
        try:
            broker = Broker.objects.get(user=request.user)
        except Exception:
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
        # print("************ Get Package Query")
        # exe_response_type_0, exe_response_description_0 = MCI().behsa_package_query()

        print("************ Get Package Credit")
        exe_response_type_2, exe_response_description_2 = MCI().behsa_package_credit()

        print("************ Get Charge Credit")
        exe_response_type_1, exe_response_description_1 = MCI().behsa_charge_credit()

        # update_mci_packages()

        data = {
            "message": "Request successfully executed",
            "message_fa": "درخواست با موفقیت اجرا شد",
            # "exe_response_type_0": exe_response_type_0,
            # "exe_response_description_0": exe_response_description_0,
            "exe_response_type_1": exe_response_type_1,
            "exe_response_description_1": exe_response_description_1,
            "exe_response_type_2": exe_response_type_2,
            "exe_response_description_2": exe_response_description_2
        }
        return Response(data, status=status.HTTP_200_OK)
