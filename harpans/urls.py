from django.conf import settings
from django.urls import include, path
from django.contrib import admin
from django.conf.urls.static import static
from django.http import HttpResponse

from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from contact.views import contact_form_submit, instagram_feed, callback_request
from blog.views import blog_subscribe, blog_unsubscribe


# --- Extra “utility” views ---

def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow:",
        # Blocka admin-paneler
        "Disallow: /harpans-kontor/",
        "Disallow: /harpans-django-backend/",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def security_txt(request):
    lines = [
        "Contact: mailto:info@harpans.se",
        "Preferred-Languages: sv, en",
        # Lägg till om ni får en sida om säkerhet/policy:
        # "Policy: https://harpans.se/sakerhet/",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


# --- URL patterns ---

urlpatterns = [
    path("harpans-django-backend/", admin.site.urls),
    path("harpans-kontor/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("api/blog/subscribe/", blog_subscribe, name="blog_subscribe"),
    path("blog/unsubscribe/<str:token>/", blog_unsubscribe, name="blog_unsubscribe"),

    # API endpoints
    path("api/contact/", contact_form_submit, name="contact_submit"),
    path("api/callback-request/", callback_request, name="callback_request"),
    path("api/instagram/", instagram_feed, name="instagram_feed"),

    # robots.txt & security.txt
    path("robots.txt", robots_txt, name="robots_txt"),
    path(".well-known/security.txt", security_txt, name="security_txt"),
]


# --- Debug / static i dev ---

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


# --- Wagtail pages (måste ligga sist) ---

urlpatterns += [
    path("", include(wagtail_urls)),
]
