import jdatetime
from django.contrib.auth.models import User
from rest_framework import permissions, authentication, status
import pandas as pd
from rest_framework.response import Response
from rest_pandas import PandasExcelRenderer

from accounts.views import BaseAPIView
from transactions.models import TopUp, PackageRecord


class ChargeSaleReportView(PandasSimpleView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.BasicAuthentication,)
    renderer_classes = [PandasExcelRenderer]

    def get_data(self, request, *args, **kwargs):
        user = request.user
        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')

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

        from_date_list = from_date.split('-')
        to_date_list = to_date.split('-')
        from_date_mod = jdatetime.date(int(from_date_list[0]), int(from_date_list[1]), int(from_date_list[2]))
        to_date_mod = jdatetime.date(int(to_date_list[0]), int(to_date_list[1]), int(to_date_list[2]))

        data = TopUp.report(user.broker, from_date_mod, to_date_mod)

        return pd.DataFrame.from_dict(data=data)


class PackageSaleReportView(BaseAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.BasicAuthentication,)

    @staticmethod
    def get_data(request):
        user = request.user
        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')

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

        from_date_list = from_date.split('-')
        to_date_list = to_date.split('-')
        from_date_mod = jdatetime.date(int(from_date_list[0]), int(from_date_list[1]), int(from_date_list[2]))
        to_date_mod = jdatetime.date(int(to_date_list[0]), int(to_date_list[1]), int(to_date_list[2]))

        data = PackageRecord.report(user.broker, from_date_mod, to_date_mod)

        return pd.DataFrame.from_dict(data=data)
