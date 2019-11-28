from django.contrib import admin

from transactions.models import TopUp, PackageRecord, ProvidersToken, Package


class TopUpAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'broker', 'tell_num', 'tell_charger', 'amount', 'timestamp', 'state',
        'charge_type', 'call_response_type', 'exe_response_type', 'execution_time',
        'provider_id', 'bank_code', 'card_number', 'card_type',
        # 'call_response_description', 'exe_response_description'
    ]
    # all
    readonly_fields = [
        'id', 'broker', 'tell_num', 'tell_charger', 'amount', 'timestamp', 'state',
        'charge_type', 'call_response_type', 'exe_response_type', 'execution_time',
        'provider_id', 'bank_code', 'card_number', 'card_type',
        'call_response_description', 'exe_response_description'
    ]
    list_filter = []
    search_fields = []

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request=request)
        return super().get_queryset(request=request).filter(broker__user=request.user)


class PackageRecordAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'broker', 'tell_num', 'tell_charger', 'amount', 'timestamp', 'state',
        'package', 'call_response_type', 'exe_response_type', 'execution_time',
        'provider_id', 'bank_code', 'card_number', 'card_type',
        # 'call_response_description', 'exe_response_description'
    ]
    # all
    readonly_fields = [
        'id', 'broker', 'tell_num', 'tell_charger', 'amount', 'timestamp', 'state',
        'package', 'call_response_type', 'exe_response_type', 'execution_time',
        'provider_id', 'bank_code', 'card_number', 'card_type',
        'call_response_description', 'exe_response_description'
    ]
    list_filter = []
    search_fields = []

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request=request)
        return super().get_queryset(request=request).filter(broker__user=request.user)

    def amount(self, obj):
        return obj.package.amount
    amount.allow_tags = True


class PackageAdmin(admin.ModelAdmin):
    list_display = ['package_type', 'name', 'amount', 'creator', 'timestamp', 'active', 'description']

    def save_model(self, request, obj, form, change):
        obj.creator = request.user
        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['package_type', 'creator', 'timestamp']
        else:
            return ['creator', 'timestamp']

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request=request)
        return super().get_queryset(request=request).filter(user=request.user)


admin.site.register(TopUp, TopUpAdmin)
admin.site.register(ProvidersToken)
admin.site.register(PackageRecord, PackageRecordAdmin)
admin.site.register(Package, PackageAdmin)
