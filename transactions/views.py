from django.db import transaction
# from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from accounts.views import BaseAPIView
from interface.API import MCI
from accounts.models import Broker
from transactions.models import TopUp, PackageRecord, TopUpState, Package
from transactions.serializers import PackageSerializer


class ChargeCallSaleView(BaseAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def post(request):
        try:
            amount = request.data.get('amount')
            broker = Broker.objects.get(user=request.user)
            tell_num = request.data.get('tell_num')
            tell_charger = request.data.get('tell_charger')
            charge_type = request.data.get('charge_type')
            top_up = TopUp.create(
                amount=amount,
                broker=broker,
                tell_num=tell_num,
                tell_charger=tell_charger,
                charge_type=charge_type
            )
        except Exception as e:
            data = {
                "message": str(e),
                "message_fa": "خطا: پارامترهای غیر معتبر",
                "code": -10,
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        if broker.credit < top_up.amount:
            data = {
                "message": "error: Brokers balance is insufficient",
                "message_fa": "اعتبار کارگزار کافی نیست.",
                "code": -20,
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
                "code": 0,
                "provider_id": top_up.provider_id
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            data = {
                "message": "error: failed to submit request",
                "message_fa": "خطا در ثبت درخواست",
                "code": -11,
                "response_type": top_up.call_response_type,
                "response_description": top_up.call_response_description
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
            top_up = TopUp.objects.get(provider_id=provider_id,broker=broker)
            if top_up.state == TopUpState.CALLED.value:
                top_up.before_execute(
                    bank_code=bank_code,
                    card_number=card_number,
                    card_type=card_type
                )
            else:
                data = {
                    "message": "error: invalid provider_id: could not find a record with valid call sale",
                    "message_fa": "خطا: پارامتر provider_id غیر معتبر",
                    "code": -19,
                }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

        except Exception:
            data = {
                "message": "error: invalid parameters",
                "message_fa": "خطا: پارامترهای غیر معتبر",
                "code": -10,
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        if broker.credit < top_up.amount:
            data = {
                "message": "error: Brokers balance is insufficient",
                "message_fa": "اعتبار کارگزار کافی نیست.",
                "code": -20,
            }
            return Response(data, status=status.HTTP_200_OK)

        if broker.active is False:
            data = {
                "message": "error: Brokers is deactive",
                "message_fa": "کارگذار غیرفعال است.",
                "code": -21,
            }
            return Response(data, status=status.HTTP_200_OK)

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
                "code": 0,
                # "provider_id": top_up.provider_id
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            data = {
                "message": "error: failed to execute request",
                "message_fa": "خطا در اجرای درخواست",
                "code": -18,
                "exe_response_type": top_up.exe_response_type,
                "exe_response_description": top_up.exe_response_description
            }
            return Response(data, status=status.HTTP_200_OK)


class PackageCallSaleView(BaseAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def post(request):
        try:
            # amount = int(request.data.get('amount'))
            broker = Broker.objects.get(user=request.user)
            tell_num = request.data.get('tell_num')
            tell_charger = request.data.get('tell_charger')
            package_type = request.data.get('package_type')
            package = Package.objects.get(package_type=package_type)
            package_log = PackageRecord.create(
                # amount=amount,
                broker=broker,
                tell_num=tell_num,
                tell_charger=tell_charger,
                package_id=package.pk
            )
        except Exception as e:
            data = {
                "message": str(e),
                "message_fa": "خطا: پارامترهای غیر معتبر",
                "code": -10,
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        if broker.credit < package_log.package.amount:
            data = {
                "message": "error: Brokers balance is insufficient",
                "message_fa": "اعتبار کارگزار کافی نیست.",
                "code": -20,
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
                "code": 0,
                "provider_id": package_log.provider_id
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            data = {
                "message": "error: failed to submit request",
                "message_fa": "خطا در ثبت درخواست",
                "code": -11,
                "response_type": package_log.call_response_type,
                "response_description": package_log.call_response_description
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
            if package_log.state == TopUpState.CALLED.value:
                package_log.before_execute(
                    bank_code=bank_code,
                    card_number=card_number,
                    card_type=card_type
                )
            else:
                data = {
                    "message": "error: invalid provider_id: could not find a record with valid call sale",
                    "message_fa": "خطا: پارامتر provider_id غیر معتبر",
                    "code": -19,
                }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

        except Exception:
            data = {
                "message": "error: invalid parameters",
                "message_fa": "خطا: پارامترهای غیر معتبر",
                "code": -10,
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        if broker.credit < package_log.package.amount:
            data = {
                "message": "error: Brokers balance is insufficient",
                "message_fa": "اعتبار کارگزار کافی نیست.",
                "code": -20,
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
                "code": 0,
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            data = {
                "message": "error: failed to execute request",
                "message_fa": "خطا در اجرای درخواست",
                "code": -18,
                "exe_response_type": package_log.exe_response_type,
                "exe_response_description": package_log.exe_response_description
            }
            return Response(data, status=status.HTTP_200_OK)


class BrokerCreditView(BaseAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def post(request):
        try:
            broker = Broker.objects.get(user=request.user)
        except Exception:
            data = {
                "message": "error: Invalid Broker",
                "message_fa": "خطا: کارگزار نامعتبر است.",
                "code": -22,
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        if broker.active is False:
            data = {
                "message": "error: Brokers is deactive",
                "message_fa": "کارگذار غیرفعال است.",
                "code": -21,
            }
            return Response(data, status=status.HTTP_200_OK)

        data = {
                "message": "Request successfully executed",
                "message_fa": "درخواست با موفقیت اجرا شد",
                "code": 0,
                "Credit": broker.credit
        }
        return Response(data, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(["GET"])
def active_packages(request):
    actives = PackageSerializer(Package.objects.filter(active=True), many=True).data
    data = {'message': 'success: active packages',
            'data': actives
            }
    return Response(data, status=status.HTTP_200_OK)
