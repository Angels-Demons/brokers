from rest_framework import permissions
import pandas as pd

from accounts.views import BaseAPIView


class ChargeCallSaleView(BaseAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def get(request):
        from_date = request.data.get('from_date')
        to_date = request.data.get('to_date')

        data = None  # data type should be a list of jsons with charge_type as row key,
                     # ex:[{'charge_type': 1, ...}, {'charge_type': 2, ...}]
                     # data is the output report

        return pd.DataFrame.from_dict(data=data)
