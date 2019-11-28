from django.contrib import admin

from transactions.models import TopUp, PackageRecord, ProvidersToken


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


admin.site.register(TopUp, TopUpAdmin)
admin.site.register(ProvidersToken)
admin.site.register(PackageRecord)
