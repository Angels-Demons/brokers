from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.humanize.templatetags.humanize import intcomma
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from transactions.models import TopUp, PackageRecord, ProvidersToken, Package


def is_admin(user):
    (admin_group, created) = Group.objects.get_or_create(name='admin')
    if user in admin_group.user_set.all():
        return True
    return False


class TopUpResource(resources.ModelResource):
    class Meta:
        model = TopUp


class PackageLogResource(resources.ModelResource):
    class Meta:
        model = PackageRecord


class PackageResource(resources.ModelResource):
    class Meta:
        model = Package


class TopUpAdmin(ImportExportModelAdmin):
    resource_class = TopUpResource
    list_display = [
        'id', 'broker', 'operator', 'tell_num', 'tell_charger', 'amount_display', 'timestamp', 'state',
        'charge_type', 'call_response_type', 'exe_response_type', 'execution_time',
        'provider_id', 'bank_code', 'card_number', 'card_type',
        # 'call_response_description', 'exe_response_description'
    ]

    # all
    readonly_fields = [
        'id', 'broker', 'operator', 'tell_num', 'tell_charger', 'amount_display', 'timestamp', 'state',
        'charge_type', 'call_response_type', 'exe_response_type', 'execution_time',
        'provider_id', 'bank_code', 'card_number', 'card_type',
        'call_response_description', 'exe_response_description'
    ]

    list_filter = ['charge_type', 'broker', 'state']
    search_fields = ['tell_num', 'tell_charger']

    def get_exclude(self, request, obj=None):
        if obj:
            return ['amount']
        else:
            return []

    def amount_display(self, obj):
        return intcomma(obj.amount)

    amount_display.allow_tags = True
    amount_display.short_description = "Amount (Rials)"

    def get_queryset(self, request):
        if request.user.is_superuser or is_admin(request.user):
            return super().get_queryset(request=request)
        return super().get_queryset(request=request).filter(broker__user=request.user)


class PackageRecordAdmin(ImportExportModelAdmin):
    resource_class = PackageLogResource
    list_display = [
        'id', 'broker', 'tell_num', 'tell_charger', 'amount_display', 'timestamp', 'state',
        'package', 'call_response_type', 'exe_response_type', 'execution_time',
        'provider_id', 'bank_code', 'card_number', 'card_type',
        # 'call_response_description', 'exe_response_description'
    ]
    # all
    readonly_fields = [
        'id', 'broker', 'tell_num', 'tell_charger', 'amount_display', 'timestamp', 'state',
        'package', 'call_response_type', 'exe_response_type', 'execution_time',
        'provider_id', 'bank_code', 'card_number', 'card_type',
        'call_response_description', 'exe_response_description'
    ]
    list_filter = ['package', 'broker', 'state']
    search_fields = ['tell_num', 'tell_charger']

    def get_exclude(self, request, obj=None):
        if obj:
            return ['amount']
        else:
            return []

    def amount_display(self, obj):
        try:
            return intcomma(obj.amount)
        except:
            return 0

    amount_display.allow_tags = True
    amount_display.short_description = "Amount (Rials)"

    def get_queryset(self, request):
        if request.user.is_superuser or is_admin(request.user):
            return super().get_queryset(request=request)
        return super().get_queryset(request=request).filter(broker__user=request.user)

    # def amount(self, obj):
    #     try:
    #         return intcomma(obj.package.amount)
    #     except AttributeError:
    #         return 0
    # amount.allow_tags = True
    # amount.short_description = "Price (Rials)"


class PackageAdmin(ImportExportModelAdmin):
    resource_class = PackageResource
    list_display = ['operator', 'package_type', 'name', 'price_display', 'system', 'creator', 'timestamp', 'active', 'description']

    def price_display(self, obj):
        return intcomma(obj.amount)

    price_display.allow_tags = True
    price_display.short_description = "Price (Rials)"

    def save_model(self, request, obj, form, change):
        obj.creator = request.user
        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['operator', 'package_type', 'creator', 'timestamp']
        else:
            return ['creator', 'timestamp']

    # def get_queryset(self, request):
    #     if request.user.is_superuser:
    #         return super().get_queryset(request=request)
    #     return super().get_queryset(request=request).filter(user=request.user)


admin.site.register(TopUp, TopUpAdmin)
admin.site.register(ProvidersToken)
admin.site.register(PackageRecord, PackageRecordAdmin)
admin.site.register(Package, PackageAdmin)
