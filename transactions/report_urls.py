from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from transactions.report_views import ChargeSaleReportView


urlpatterns = {
    url(r'^ChargeSaleReport', ChargeSaleReportView.as_view()),

}
urlpatterns = format_suffix_patterns(urlpatterns)
