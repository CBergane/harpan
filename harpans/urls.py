from django.conf import settings
from django.urls import include, path
from django.contrib import admin
from django.conf.urls.static import static

from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from contact.views import contact_form_submit, instagram_feed

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    
    # API endpoints
    path('api/contact/', contact_form_submit, name='contact_submit'),
    path('api/instagram/', instagram_feed, name='instagram_feed'),
]

#if settings.DEBUG:
# #    import debug_toolbar
#    urlpatterns = [
# #        path('__debug__/', include(debug_toolbar.urls)),
#    ] + urlpatterns
#    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
#
# Wagtail pages - måste vara sist
urlpatterns = urlpatterns + [
    path("", include(wagtail_urls)),
]
