from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.shortcuts import redirect

from accounts.models import Broker, BalanceIncrease
from rest_framework.response import Response


class BrokerAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'username', 'creator', 'credit', 'active', 'timestamp', 'email']

    def save_model(self, request, obj, form, change):
        if obj.id:
            super().save_model(request, obj, form, change)
            return

        (brokers_group, created) = Group.objects.get_or_create(name='brokers')
        if created:
            # Modify: determine the group perms
            pass  
        print(created)
        print(brokers_group)
        obj.creator = request.user
        user = User.objects.create_user(
            username=obj.username,
            email=obj.email,
            password=obj.username + "pass",
            is_staff=True,
        )

        brokers_group.user_set.add(user)
        obj.user = user
        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['username']
        else:
            return []

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request=request)
        return super().get_queryset(request=request).filter(user=request.user)


class BalanceIncreaseAdmin(admin.ModelAdmin):
    list_display = ['broker', 'creator', 'amount', 'comment', 'success', 'timestamp']

    def save_model(self, request, obj, form, change):
        obj.creator = request.user
        former_balance = obj.broker.credit
        obj.broker.credit += obj.amount
        obj.broker.save()
        if former_balance + obj.amount == obj.broker.credit:
            obj.success = True
            super().save_model(request, obj, form, change)
        else:
            super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['amount', 'broker']
        else:
            return []

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request=request)
        return super().get_queryset(request=request).filter(broker__user=request.user)


admin.site.register(Broker, BrokerAdmin)
admin.site.register(BalanceIncrease, BalanceIncreaseAdmin)
