from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from transactions.report_views import ChargeSaleReportView, PackageSaleReportView

urlpatterns = {
    url(r'^ChargeSaleReport', ChargeSaleReportView.as_view(), name='ChargeSaleReport'),
    url(r'^PackageSaleReport', PackageSaleReportView.as_view(), name='PackageSaleReport'),
}
urlpatterns = format_suffix_patterns(urlpatterns)
