from django.contrib import admin
from django.contrib.auth.models import User, Permission
from django.contrib.auth.models import Group
from django.shortcuts import redirect

from accounts.models import Broker, BalanceIncrease, OperatorAccess
from rest_framework.response import Response

from transactions.enums import CreditType


class AccessInline(admin.TabularInline):
    model = OperatorAccess
    extra = 0

    def get_readonly_fields(self, request, obj=None):
        if obj:
            print('obj')
            return ['operator', 'credit', 'top_up_credit', 'package_credit',]
        else:
            print('none')
            return ['credit', 'top_up_credit', 'package_credit']


class OperatorAccessAdmin(admin.ModelAdmin):
    list_display = ['broker', 'operator', 'active', 'general_credit_access', 'top_up_access', 'package_access',
                    'credit', 'top_up_credit', 'package_credit',
                    'last_editor', 'timestamp', 'comment']

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['broker', 'operator',
                    'credit', 'top_up_credit', 'package_credit',
                    'last_editor', 'timestamp']
        else:
            return ['credit', 'top_up_credit', 'package_credit',
                    'last_editor', 'timestamp']

    def save_model(self, request, obj, form, change):
        obj.last_editor = request.user
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request=request)
        return super().get_queryset(request=request).filter(user=request.user)


class BrokerAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'name', 'username', 'creator', 'credit', 'active', 'timestamp', 'email']
    search_fields = ['name', 'username']
    list_filter = ['active']

    inlines = [
        AccessInline,
    ]

    def save_model(self, request, obj, form, change):
        if obj.id:
            super().save_model(request, obj, form, change)
            obj.user.is_active = obj.active
            obj.user.save()
            return

        (brokers_group, created) = Group.objects.get_or_create(name='brokers')
        if created:
            # can_fm_list = Permission.objects.get(name='can_fm_list')
            # newgroup.permissions.add(can_fm_list)
            # Modify: determine the group perms
            pass
        obj.creator = request.user
        user = User.objects.create_user(
            username=obj.username,
            email=obj.email,
            password=obj.username + "pass",
            is_staff=True,
            is_active=obj.active
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
    list_display = ['broker', 'creator', 'amount', 'operator', 'credit_type', 'comment', 'success', 'timestamp']

    def save_model(self, request, obj, form, change):
        obj.creator = request.user
        # try:
        #     operator_access = OperatorAccess.objects.get(operator=obj.operator, broker=obj.broker)
        #     obj.success, obj.error = operator_access.increase_balance(obj)
        # except Exception as e:
        #     obj.error = e.__str__()
        #     print(e)
        super().save_model(request, obj, form, change)

        # obj.creator = request.user
        # former_balance = obj.broker.credit
        # obj.broker.credit += obj.amount
        # obj.broker.save()
        # if former_balance + obj.amount == obj.broker.credit:
        #     obj.success = True
        #     super().save_model(request, obj, form, change)
        # else:
        #     super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['amount', 'broker', 'success']
        else:
            return ['success']

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request=request)
        return super().get_queryset(request=request).filter(broker__user=request.user)


admin.site.register(Broker, BrokerAdmin)
admin.site.register(BalanceIncrease, BalanceIncreaseAdmin)
admin.site.register(OperatorAccess, OperatorAccessAdmin)
