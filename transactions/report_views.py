from django.contrib.auth.models import User
from rest_framework import permissions, authentication, status
import pandas as pd
from rest_framework.response import Response

from accounts.views import BaseAPIView
from transactions.models import TopUp, PackageRecord


class ChargeSaleReportView(BaseAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.CSRFCheck,)

    @staticmethod
    def get(request):
        user = request.user
        from_date = request.data.get('from_date')
        to_date = request.data.get('to_date')

        data = {}
        if not from_date:
            data["message"] = "'from_date' is not provided."
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        if not to_date:
            data["message"] = "'to_date' is not provided."
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        if not user.broker:
            data["message"] = "user is not a broker."
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        data = TopUp.report(user.broker, from_date, to_date)

        return pd.DataFrame.from_dict(data=data)


class PackageSaleReportView(BaseAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.CSRFCheck,)

    @staticmethod
    def get(request):
        user = request.user
        from_date = request.data.get('from_date')
        to_date = request.data.get('to_date')

        data = {}
        if not from_date:
            data["message"] = "'from_date' is not provided."
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        if not to_date:
            data["message"] = "'to_date' is not provided."
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        if not user.broker:
            data["message"] = "user is not a broker."
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        data = PackageRecord.report(user.broker, from_date, to_date)

        return pd.DataFrame.from_dict(data=data)
