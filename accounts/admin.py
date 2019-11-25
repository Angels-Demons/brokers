from django.contrib import admin
from django.contrib.auth.models import UserManager, User

from accounts.models import Broker, BalanceIncrease


class BrokerAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'creator', 'credit', 'timestamp', 'email']

    def save_model(self, request, obj, form, change):
        obj.creator = request.user
        user = User.objects.create_user(
            username=obj.name,
            email=obj.email,
            password=obj.name + "pass",
            is_staff=True,
        )
        # Modify: determine the group
        obj.user = user
        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['name']
        else:
            return []


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


admin.site.register(Broker, BrokerAdmin)
admin.site.register(BalanceIncrease, BalanceIncreaseAdmin)
