from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel
from core.models import BasePage
from wagtail.admin.panels import FieldPanel, InlinePanel


class ContactPage(BasePage):
    """Kontaktsida"""
    
    intro = RichTextField(blank=True, verbose_name="Introduktion")
    
    # Kontaktinfo
    address = models.TextField(blank=True, verbose_name="Adress")
    phone = models.CharField(max_length=50, blank=True, verbose_name="Telefon")
    email = models.EmailField(blank=True, verbose_name="E-post")
    
    # Öppettider
    opening_hours = RichTextField(
        blank=True,
        verbose_name="Öppettider",
        help_text="T.ex. Mån-Fre: 08:00-17:00"
    )
    
    # GDPR
    gdpr_text = RichTextField(
        default="Jag godkänner att mina uppgifter behandlas enligt GDPR",
        verbose_name="GDPR-text"
    )
    
    hero_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True, blank=True, on_delete=models.SET_NULL,
        related_name='+', verbose_name="Hero-bild"
    )

    content_panels = Page.content_panels + [
        FieldPanel('hero_image'),
        FieldPanel('intro'),
        FieldPanel('address'),
        FieldPanel('phone'),
        FieldPanel('email'),
        FieldPanel('opening_hours'),
        FieldPanel('gdpr_text'),
    ]
    
    class Meta:
        verbose_name = "Kontaktsida"


class ContactSubmission(models.Model):
    """Sparar kontaktformulär-inlämningar"""
    
    page = models.ForeignKey(
        ContactPage,
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    
    name = models.CharField(max_length=255, verbose_name="Namn")
    email = models.EmailField(verbose_name="E-post")
    phone = models.CharField(max_length=50, blank=True, verbose_name="Telefon")
    subject = models.CharField(max_length=255, blank=True, verbose_name="Ämne")
    message = models.TextField(verbose_name="Meddelande")
    
    gdpr_consent = models.BooleanField(
        default=False,
        verbose_name="GDPR-samtycke"
    )
    
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name="Inskickat")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-submitted_at']
        verbose_name = "Kontaktförfrågan"
        verbose_name_plural = "Kontaktförfrågningar"
    
    def __str__(self):
        return f"{self.name} - {self.submitted_at.strftime('%Y-%m-%d %H:%M')}"