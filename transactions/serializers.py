from rest_framework import serializers

from transactions.models import Package, Operator


class PackageSerializer(serializers.ModelSerializer):
    operator_name = serializers.SerializerMethodField('operator_name_method')

    def operator_name_method(self, obj):
        return Operator.farsi(obj.operator)

    class Meta:
        model = Package
        fields = ['package_type', 'operator', 'name', 'amount','system', 'description', 'operator_name','package_duration']


