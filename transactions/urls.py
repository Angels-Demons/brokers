from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from transactions.views import *


urlpatterns = {
    url(r'^ChargeCallSale/$', ChargeCallSaleView.as_view()),
    url(r'^ChargeExeSale/$', ChargeExeSaleView.as_view()),
    url(r'^PackageCallSale/$', PackageCallSaleView.as_view()),
    url(r'^PackageExeSale/$', PackageExeSaleView.as_view()),

}
urlpatterns = format_suffix_patterns(urlpatterns)
