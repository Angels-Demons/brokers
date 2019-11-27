from django.db import transaction
# from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions, status
from rest_framework.response import Response
from accounts.views import BaseAPIView
from interface.API import MCI
from accounts.models import Broker
from transactions.models import TopUp


class CallSaleView(BaseAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def post(request):
        with transaction.atomic():
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

            call_response_type, call_response_description = MCI().call_sale(
                top_up.tell_num,
                top_up.tell_charger,
                top_up.amount,
                top_up.charge_type,
            )
            success = top_up.after_call(call_response_type, call_response_description)
            if success:
                data = {
                    "message": "success: request successfully submitted",
                    "message_fa": "موفقیت: درخواست با موفقیت ثبت شد",
                    "code": 0,
                    "provider_id": top_up.provider_id
                }
                return Response(data, status=status.HTTP_200_OK)
            else:
                data = {
                    "message": "error: failed to submit request",
                    "message_fa": "خطا: خطا در ثبت درخواست",
                    "code": -11,
                    "response_type": top_up.call_response_type,
                    "response_description": top_up.call_response_description
                }
                return Response(data, status=status.HTTP_200_OK)


class ExeSaleView(BaseAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def post(request):
        with transaction.atomic():
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
            except Exception:
                data = {
                    "message": "error: invalid parameters",
                    "message_fa": "خطا: پارامترهای غیر معتبر",
                    "code": -10,
                }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

            call_response_type, call_response_description = MCI().call_sale(
                top_up.tell_num,
                top_up.tell_charger,
                top_up.amount,
                top_up.charge_type,
            )
            success = top_up.after_call(call_response_type, call_response_description)
            if success:
                data = {
                    "message": "success: request successfully submitted",
                    "message_fa": "موفقیت: درخواست با موفقیت ثبت شد",
                    "code": 0,
                    "provider_id": top_up.provider_id
                }
                return Response(data, status=status.HTTP_200_OK)
            else:
                data = {
                    "message": "error: failed to submit request",
                    "message_fa": "خطا: خطا در ثبت درخواست",
                    "code": -11,
                    "call_response_type": top_up.call_response_type,
                    "call_response_description": top_up.call_response_description
                }
                return Response(data, status=status.HTTP_200_OK)
