# blog/signals.py
from django.dispatch import receiver
from django.conf import settings
from django.core.mail import get_connection, EmailMessage
from django.template.loader import render_to_string
from django.urls import reverse

from wagtail.signals import page_published

from .models import BlogPost, BlogSubscriber, BlogPostNotification


@receiver(page_published)
def send_blogpost_notifications(sender, instance, **kwargs):
    """
    Skickas varje gång en sida publiceras.
    Vi filtrerar på BlogPost, kollar om vi ska skicka, och ser till
    att varje post bara får ETT utskick (via BlogPostNotification).
    """
    # Bara blogginlägg
    if not isinstance(instance, BlogPost):
        return

    # Om kunden bockar ur "Skicka prenumerationsmail"
    if not instance.send_notification:
        return

    # Har vi redan skickat för den här posten?
    if BlogPostNotification.objects.filter(post=instance).exists():
        return

    # Hämta aktiva prenumeranter
    subscribers = BlogSubscriber.objects.filter(active=True)
    if not subscribers.exists():
        return

    # Bygg full URL till inlägget
    url_parts = instance.get_url_parts()
    if url_parts:
        _, root_url, relative_url = url_parts
        post_url = root_url + relative_url
    else:
        base = getattr(settings, "BASE_URL", "").rstrip("/") or "https://harpans.se"
        post_url = f"{base}{instance.url}"

    # För unsubscribe-länkar behövs också root_url
    if url_parts:
        _, root_url, _ = url_parts
    else:
        root_url = getattr(settings, "BASE_URL", "").rstrip("/")

    # Förbered mail
    connection = get_connection()
    messages = []

    for sub in subscribers:
        unsubscribe_path = reverse("blog_unsubscribe", args=[sub.unsubscribe_token])
        unsubscribe_url = root_url + unsubscribe_path

        body = render_to_string("blog/email/new_post.txt", {
            "post": instance,
            "post_url": post_url,
            "unsubscribe_url": unsubscribe_url,
        })

        msg = EmailMessage(
            subject=f"Nytt inlägg: {instance.title}",
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[sub.email],
        )
        messages.append(msg)

    # Skicka alla mail via samma SMTP-connection
    connection.send_messages(messages)

    # Markera att vi har skickat utskick för denna post
    BlogPostNotification.objects.create(post=instance)
