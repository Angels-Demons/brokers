from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
                  url(r'^dash/', admin.site.urls),
                  url(r'^v1/', include('accounts.urls')),
                  url(r'^v1/', include('transactions.urls')),
                  url(r'^jet/', include('jet.urls', 'jet')),
                  url(r'^jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL,
                                                                                           document_root=settings.MEDIA_ROOT)
