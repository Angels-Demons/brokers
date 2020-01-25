from rest_framework import serializers

from transactions.models import Package, Operator
from accounts.models import OperatorAccess


class OperatorAccessSerializer(serializers.ModelSerializer):
    general_credit = serializers.CharField(source='credit')
    class Meta:
        model = OperatorAccess
        fields = ['operator', 'general_credit', 'top_up_credit', 'package_credit']


class PackageSerializer(serializers.ModelSerializer):
    operator_name = serializers.SerializerMethodField('operator_name_method')
    # PackageCostWithVat = serializers.SerializerMethodField('get_PackageCostWithVat')

    def operator_name_method(self, obj):
        return Operator.farsi(obj.operator)

    # def get_PackageCostWithVat(self, obj):
    #     return int(1.09 * int(obj.amount))

    class Meta:
        model = Package
        fields = ['package_type', 'operator', 'name', 'amount', 'PackageCostWithVat', 'system', 'description',
                  'operator_name', 'package_duration']


