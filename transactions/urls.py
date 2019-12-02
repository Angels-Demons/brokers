from django.conf.urls import url
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from transactions.views import *


urlpatterns = {
    url(r'^TestApi58', TestApi58.as_view()),
    url(r'^ChargeCallSale', ChargeCallSaleView.as_view()),
    url(r'^ChargeExeSale', ChargeExeSaleView.as_view()),
    url(r'^PackageCallSale', PackageCallSaleView.as_view()),
    url(r'^PackageExeSale', PackageExeSaleView.as_view()),
    url(r'^BrokerCredit', BrokerCreditView.as_view()),
    path('active_packages', active_packages, name='active_packages'),

}
urlpatterns = format_suffix_patterns(urlpatterns)
