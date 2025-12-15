# blog/models.py

import secrets
from django.db import models
from django.utils import timezone
from django.urls import reverse

from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel
from wagtail.search import index
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.documents.models import Document

from core.models import BasePage


class BlogIndexPage(BasePage):
    hero_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Hero-bild'
    )

    hero_video = models.ForeignKey(
        Document,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('hero_image'),
        FieldPanel('hero_video'),
        FieldPanel('intro'),
    ]

    def get_posts(self):
        return BlogPost.objects.live().descendant_of(self).order_by('-date')

    def get_context(self, request):
        ctx = super().get_context(request)
        ctx['posts'] = self.get_posts()
        return ctx

    class Meta:
        verbose_name = "Blogg"


class BlogPost(BasePage):
    """Blogginlägg"""

    date = models.DateTimeField(
        "Publiceringsdatum",
        default=timezone.now
    )

    author_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Författare",
        help_text="Ange författarens namn"
    )

    intro = models.CharField(
        max_length=250,
        help_text="Kort sammanfattning (visas i listningar och SEO)",
        verbose_name="Ingress"
    )

    reading_time = models.IntegerField(
        default=5,
        verbose_name="Läsningstid (minuter)",
        help_text="Uppskattad läsningstid i minuter"
    )

    # ✅ kontroll om det ska skickas utskick
    send_notification = models.BooleanField(
        default=True,
        verbose_name="Skicka prenumerationsmail",
        help_text="Om ikryssad skickas mail till prenumeranter när inlägget publiceras första gången."
    )

    body = StreamField([
        ('heading', blocks.CharBlock(form_classname="title", label='Rubrik')),
        ('paragraph', blocks.RichTextBlock(label='Paragraf')),
        ('image', ImageChooserBlock(label='Bild')),
        ('quote', blocks.BlockQuoteBlock(label='Citat')),
        ('video', DocumentChooserBlock()),
    ], use_json_field=True, verbose_name="Innehåll")

    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('date'),
        FieldPanel('author_name'),
        FieldPanel('reading_time'),
        FieldPanel('intro'),
        FieldPanel('send_notification'),
        FieldPanel('body'),
    ]

    class Meta:
        verbose_name = "Blogginlägg"
        verbose_name_plural = "Blogginlägg"


class BlogSubscriber(models.Model):
    """Prenumerant på blogg-uppdateringar."""
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    # enkel token för unsubscribe-länk
    unsubscribe_token = models.CharField(
        max_length=64,
        unique=True,
        editable=False,
    )

    def save(self, *args, **kwargs):
        if not self.unsubscribe_token:
            self.unsubscribe_token = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)

    def get_unsubscribe_url(self):
        return reverse("blog_unsubscribe", args=[self.unsubscribe_token])

    def __str__(self):
        return self.email


class BlogPostNotification(models.Model):
    """
    Logg: Har vi redan skickat ut den här posten till prenumeranter?
    En rad per BlogPost -> då vet vi att vi inte ska maila igen.
    """
    post = models.OneToOneField(
        BlogPost,
        on_delete=models.CASCADE,
        related_name="notification_entry",
    )
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.post.title} @ {self.sent_at:%Y-%m-%d %H:%M}"
