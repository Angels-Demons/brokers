from rest_framework import serializers

from transactions.models import Package


class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = ['package_type', 'name', 'amount', 'description']
