from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK,
    HTTP_401_UNAUTHORIZED,
)
from interface.API import MCI
from accounts.models import Broker
from transactions.models import TopUp


@csrf_exempt
@api_view(["POST"])
def mcci_call_sale(request):
    try:
        amount = request.POST['amount']
        broker = Broker.objects.get(user=request.user)
        tell_num = request.POST['tell_num']
        tell_charger = request.POST['tell_charger']
        charge_type = request.POST['charge_type']
        top_up = TopUp.create(
            amount=amount,
            broker=broker,
            tell_num=tell_num,
            tell_charger=tell_charger,
            charge_type=charge_type
        )
        call_response_type, call_response_description = MCI.call_sale(
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
                "code": 200,
                "status": 200,
                "provider_id": top_up.provider_id
            }
            return Response(data, status=HTTP_200_OK)
        else:
            data = {
                "message": "error: failed to submit request",
                "message_fa": "خطا: خطا در ثبت درخواست",
                "code": 301,
                "status": 200,
                "call_response_type": top_up.call_response_type,
                "call_response_description": top_up.call_response_description
            }
            return Response(data, status=HTTP_200_OK)

    except Exception:
        data = {
            "message": "error: invalid parameters",
            "message_fa": "خطا: پارامترهای غیر معتبر",
            "code": 301,
            "status": 400,
        }
        return Response(data, status=HTTP_400_BAD_REQUEST)
