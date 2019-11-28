from django.contrib import admin

from transactions.models import TopUp,Package,ProvidersToken

admin.site.register(TopUp)

admin.site.register(ProvidersToken)
admin.site.register(Package)
