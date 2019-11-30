from django.core.exceptions import ValidationError
from django.db import transaction
# from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from accounts.views import BaseAPIView
from interface.API import MCI
from accounts.models import Broker
from transactions.models import TopUp, PackageRecord, RecordState, Package
from transactions.serializers import PackageSerializer
from transactions.enums import ResponceCodeTypes as codes, Operator


class ChargeCallSaleView(BaseAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def post(request):
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
            top_up = TopUp.create(
                operator=operator,
                amount=amount,
                broker=broker,
                tell_num=tell_num,
                tell_charger=tell_charger,
                charge_type=charge_type
            )
        except ValidationError as e:
            data = {
                "message": str(e.messages[0]),
                "message_fa": "خطا: پارامترهای غیر معتبر",
                "code": codes.invalid_parameter,
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        if broker.credit < top_up.amount:
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

        except Exception:
            data = {
                "message": "Invalid parameters",
                "message_fa": "خطا: پارامترهای غیر معتبر",
                "code": codes.invalid_parameter,
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        if broker.credit < top_up.amount:
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
            broker.charge_for_mcci_transaction(top_up.amount)
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
            if not operator or int(operator) != Operator.MCI.value:
                data["message"] = "'operator' is not provided."
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            package = Package.objects.get(package_type=package_type, operator=operator)
            package_log = PackageRecord.create(
                broker=broker,
                tell_num=tell_num,
                tell_charger=tell_charger,
                package_id=package.pk
            )
        except ValidationError as e:
            data = {
                "message": str(e.messages[0]),
                "message_fa": "خطا: پارامترهای غیر معتبر",
                "code": codes.invalid_parameter,
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        if broker.credit < package_log.package.amount:
            package_log.state = RecordState.INITIAL_ERROR.value
            package_log.save()
            data = {
                "message": "Brokers balance is insufficient",
                "message_fa": "اعتبار کارگزار کافی نیست.",
                "code": codes.insufficient_balance,
            }
            return Response(data, status=status.HTTP_200_OK)

        call_response_type, call_response_description = MCI().package_call_sale(
            package_log.tell_num,
            package_log.tell_charger,
            package_log.package.amount,
            package_log.package.package_type,
        )
        success = package_log.after_call(call_response_type, call_response_description)
        if success:
            data = {
                "message": "Request successfully submitted",
                "message_fa": "درخواست با موفقیت ثبت شد",
                "code": codes.successful,
                "provider_id": package_log.provider_id
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            data = {
                "message": "Failed to submit request",
                "message_fa": package_log.call_response_description,
                "code": package_log.call_response_type,
            }
            return Response(data, status=status.HTTP_200_OK)


class PackageExeSaleView(BaseAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def post(request):
        try:
            broker = Broker.objects.get(user=request.user)
            provider_id = request.data.get('provider_id')
            bank_code = request.data.get('bank_code')
            card_number = request.data.get('card_number')
            card_type = request.data.get('card_type')
            package_log = PackageRecord.objects.get(provider_id=provider_id, broker=broker)
            if package_log.state == RecordState.CALLED.value:
                package_log.before_execute(
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

        except ValidationError as e:
            data = {
                "message": str(e.messages[0]),
                "message_fa": "خطا: پارامترهای غیر معتبر",
                "code": codes.invalid_parameter,
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        if broker.credit < package_log.package.amount:
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
            provider_id=package_log.provider_id,
            bank_code=package_log.bank_code,
            card_no=package_log.card_number,
            card_type=package_log.card_type
        )
        success = package_log.after_execute(exe_response_type, exe_response_description)
        if success:
            broker.charge_for_mcci_transaction(package_log.package.amount)
            data = {
                "message": "Request successfully executed",
                "message_fa": "درخواست با موفقیت اجرا شد",
                "code": codes.successful,
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            data = {
                "message": "Failed to execute request",
                "message_fa": package_log.call_response_description,
                "code": package_log.call_response_type,
            }
            return Response(data, status=status.HTTP_200_OK)


class BrokerCreditView(BaseAPIView):
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

        data = {
            "message": "Request successfully executed",
            "message_fa": "درخواست با موفقیت اجرا شد",
            "code": codes.successful,
            "credit": broker.credit
        }
        return Response(data, status=status.HTTP_200_OK)


@api_view(["GET"])
def active_packages(request):
    serialized_data = PackageSerializer(Package.objects.filter(active=True), many=True).data
    data = {
        "message": "Request successfully executed",
        "message_fa": "درخواست با موفقیت اجرا شد",
        "code": codes.successful,
        "packages": serialized_data
    }
    return Response(data, status=status.HTTP_200_OK)
