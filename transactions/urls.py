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
    url(r'^TransactionStatusInquiry', TransactionStatusInquiry.as_view()),
    url(r'^active_packages', ActivePackages.as_view()),
    url(r'^raceTest', RaceTest.as_view()),


}
urlpatterns = format_suffix_patterns(urlpatterns)
