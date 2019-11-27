from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from transactions.views import *


urlpatterns = {
    url(r'^CallSale/$', CallSaleView.as_view()),
    url(r'^ExeSale/$', ExeSaleView.as_view()),
}
urlpatterns = format_suffix_patterns(urlpatterns)
