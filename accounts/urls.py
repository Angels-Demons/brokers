from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework_jwt.views import refresh_jwt_token
from accounts.views import *

urlpatterns = {
    url(r'^BrokerLogin', BrokerLogin.as_view()),
    # url(r'^RefreshToken/', refresh_jwt_token),
}
urlpatterns = format_suffix_patterns(urlpatterns)
