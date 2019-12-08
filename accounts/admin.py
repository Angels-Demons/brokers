from django.contrib import admin
from django.contrib.auth.models import User, Permission
from django.contrib.auth.models import Group
from django.contrib.humanize.templatetags.humanize import apnumber, intcomma

from accounts.models import Broker, BalanceIncrease, OperatorAccess
from rest_framework.response import Response
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from transactions.enums import CreditType

def is_admin(user):
    (admin_group, created) = Group.objects.get_or_create(name='admin')
    if user in admin_group.user_set.all():
        return True
    return False



class BrokerResource(resources.ModelResource):
    class Meta:
        model = Broker


class BalanceIncreaseResource(resources.ModelResource):
    class Meta:
        model = BalanceIncrease


class OperatorAccessResource(resources.ModelResource):
    class Meta:
        model = OperatorAccess


class AccessInline(admin.TabularInline):
    model = OperatorAccess
    # exclude = []
    exclude = ['credit', 'top_up_credit', 'package_credit',
               'general_credit_access', 'top_up_access', 'package_access',
               'comment', 'banned_packages']
    extra = 0

    def access(self, obj):
        if obj.general_credit_access:
            return "اعتبار عمومی"
        if obj.top_up_access and obj.package_access:
            return "اعتبار شارژ و بسته"
        if obj.top_up_access:
            return "فقط اعتبار شارژ"
        if obj.package_access:
            return "فقط اعتبار بسته"
        return "بدون دسترسی"
    access.allow_tags = True
    access.admin_order_field = "general_credit_access"

    def credit_display(self, obj):
        return intcomma(obj.credit)
    credit_display.allow_tags = True
    credit_display.short_description = "credit (Rials)"

    def top_up_credit_display(self, obj):
        return intcomma(obj.top_up_credit)
    top_up_credit_display.allow_tags = True
    top_up_credit_display.short_description = "top_up credit (Rials)"

    def package_credit_display(self, obj):
        return intcomma(obj.package_credit)
    package_credit_display.allow_tags = True
    package_credit_display.short_description = "package credit (Rials)"

    def get_readonly_fields(self, request, obj=None):
        return ['access', 'operator', 'active', 'package_discount', 'top_up_discount',
                'credit_display', 'top_up_credit_display', 'package_credit_display']


class OperatorAccessAdmin(ImportExportModelAdmin):
    resource_class = OperatorAccessResource

    list_display = ['broker', 'access', 'operator', 'top_up_discount', 'package_discount', 'active',
                    # 'general_credit_access', 'top_up_access', 'package_access',
                    # 'credit', 'top_up_credit', 'package_credit',
                    'credit_display', 'top_up_credit_display', 'package_credit_display',
                    'last_editor', 'timestamp', 'comment']

    def access(self, obj):
        if obj.general_credit_access:
            return "اعتبار عمومی"
        if obj.top_up_access and obj.package_access:
            return "اعتبار شارژ و بسته"
        if obj.top_up_access:
            return "فقط اعتبار شارژ"
        if obj.package_access:
            return "فقط اعتبار بسته"
        return "بدون دسترسی"
    access.allow_tags = True
    access.admin_order_field = "general_credit_access"

    def credit_display(self, obj):
        return intcomma(obj.credit)

    credit_display.allow_tags = True
    credit_display.short_description = "credit (Rials)"

    def top_up_credit_display(self, obj):
        return intcomma(obj.top_up_credit)

    top_up_credit_display.allow_tags = True
    top_up_credit_display.short_description = "top_up credit (Rials)"

    def package_credit_display(self, obj):
        return intcomma(obj.package_credit)

    package_credit_display.allow_tags = True
    package_credit_display.short_description = "package credit (Rials)"

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['broker', 'operator', 'access',
                    'credit_display', 'top_up_credit_display', 'package_credit_display',
                    'last_editor', 'timestamp']
        else:
            return []

    def get_exclude(self, request, obj=None):
        if obj:
            return ['credit', 'top_up_credit', 'package_credit']
        else:
            return [
                'last_editor', 'timestamp',
                'credit', 'top_up_credit', 'package_credit']

    def save_model(self, request, obj, form, change):
        obj.last_editor = request.user
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        if request.user.is_superuser or is_admin(request.user):
            return super().get_queryset(request=request)
        try:
            return super().get_queryset(request=request).filter(broker=request.user.broker)
        except Exception:
            return None


class BrokerAdmin(ImportExportModelAdmin):
    resource_class = BrokerResource
    list_display = ['id', 'user', 'name', 'username', 'creator', 'active', 'timestamp', 'email']
    search_fields = ['name', 'username']

    list_filter = ['active']

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['username', 'creator', 'user', 'timestamp']
        else:
            return []

    def get_exclude(self, request, obj=None):
        if obj:
            return []
        else:
            return ['creator', 'user']

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

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request=request)
        return super().get_queryset(request=request).filter(user=request.user)


class BalanceIncreaseAdmin(ImportExportModelAdmin):
    resource_class = BalanceIncreaseResource
    list_display = ['broker', 'amount_display', 'creator', 'operator', 'credit_type', 'comment', 'success', 'timestamp']

    def save_model(self, request, obj, form, change):
        obj.creator = request.user
        super().save_model(request, obj, form, change)

    def amount_display(self, obj):
        return intcomma(obj.amount)

    amount_display.allow_tags = True
    amount_display.short_description = "Amount (Rials)"

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['comment', 'amount_display', 'creator', 'broker', 'success', 'operator', 'credit_type']
        else:
            return []

    def get_exclude(self, request, obj=None):
        if obj:
            return ['amount']
        else:
            return ['creator', 'success']

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request=request)
        return super().get_queryset(request=request).filter(broker__user=request.user)


admin.site.register(Broker, BrokerAdmin)
admin.site.register(BalanceIncrease, BalanceIncreaseAdmin)
admin.site.register(OperatorAccess, OperatorAccessAdmin)
