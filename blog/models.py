from django.db import models
from django.utils import timezone
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel
from wagtail.search import index
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from core.models import BasePage


class BlogIndexPage(BasePage):
    """Bloggens indexsida"""
    
    intro = RichTextField(blank=True, verbose_name="Introduktion")
    
    content_panels = BasePage.content_panels + [
        FieldPanel('intro'),
    ]
    
    def get_posts(self):
        return BlogPost.objects.live().descendant_of(self).order_by('-date')
    
    def get_context(self, request):
        context = super().get_context(request)
        context['posts'] = self.get_posts()
        return context
    
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
    
    body = StreamField([
        ('heading', blocks.CharBlock(form_classname="title", label='Rubrik')),
        ('paragraph', blocks.RichTextBlock(label='Paragraf')),
        ('image', ImageChooserBlock(label='Bild')),
        ('quote', blocks.BlockQuoteBlock(label='Citat')),
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
        FieldPanel('body'),
    ]
    
    class Meta:
        verbose_name = "Blogginlägg"
        verbose_name_plural = "Blogginlägg"