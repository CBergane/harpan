from django.db import models
from django.utils.text import slugify
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
import random
from core.models import BasePage


# =============================================================================
# BASE PAGE CLASS - All sidor ärver från denna
# =============================================================================
class BasePage(Page):
    """Bas-klass för alla sidor med automatisk slug-konvertering (åäö → aao)"""
    
    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        # Konvertera åäö → aao automatiskt i slug
        if self.title and not self.slug:
            self.slug = slugify(self.title, allow_unicode=False)
        elif self.slug:
            self.slug = slugify(self.slug, allow_unicode=False)
        super().save(*args, **kwargs)

# =============================================================================
# NAV SETTINGS
# =============================================================================

@register_setting
class NavigationSettings(BaseSiteSetting):
    """Globala inställningar för navigation"""
    
    # Sidor
    services_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Tjänstesida",
        help_text="Välj tjänstesidan"
    )
    
    team_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Team-sida",
        help_text="Välj team-sidan"
    )
    
    blog_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Blogg-sida",
        help_text="Välj blogg-sidan"
    )
    
    contact_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Kontakt-sida",
        help_text="Välj kontakt-sidan"
    )
    
    # Externa länkar
    booking_url = models.URLField(
        blank=True,
        verbose_name="Boknings-URL",
        help_text="URL till bokningssystem (t.ex. Calendly)"
    )
    
    portal_url = models.URLField(
        blank=True,
        default="https://kundportal.harpans.se",
        verbose_name="Kundportal-URL"
    )
    
    panels = [
        FieldPanel('services_page'),
        FieldPanel('team_page'),
        FieldPanel('blog_page'),
        FieldPanel('contact_page'),
        FieldPanel('booking_url'),
        FieldPanel('portal_url'),
    ]

    portal_url = models.URLField(
        blank=True,
        default="https://kundportal.harpans.se",
        verbose_name="Kundportal-URL"
    )

    # --- NYTT: Sociala medier ---
    linkedin_url = models.URLField(
        blank=True,
        verbose_name="LinkedIn-profil",
        help_text="Länk till företagets LinkedIn-sida"
    )

    x_url = models.URLField(
        blank=True,
        verbose_name="X (före detta Twitter)",
        help_text="Länk till företagets X-profil"
    )

    facebook_url = models.URLField(
        blank=True,
        verbose_name="Facebook-sida",
        help_text="Länk till företagets Facebook-sida"
    )

    instagram_url = models.URLField(
        blank=True,
        verbose_name="Instagram-profil",
        help_text="Länk till företagets Instagram-konto"
    )
    
    panels = [
        FieldPanel('services_page'),
        FieldPanel('team_page'),
        FieldPanel('blog_page'),
        FieldPanel('contact_page'),
        FieldPanel('booking_url'),
        FieldPanel('portal_url'),

        # NYTT: gruppera gärna sociala länkar längst ned
        MultiFieldPanel([
            FieldPanel('linkedin_url'),
            FieldPanel('x_url'),
            FieldPanel('facebook_url'),
            FieldPanel('instagram_url'),
        ], heading="Sociala medier"),
    ]
    
    class Meta:
        verbose_name = "Navigation"


# =============================================================================
# HOME PAGE - MED OM OSS-SEKTION OCH SLUMPMÄSSIGT TEAM
# =============================================================================
class HomePage(BasePage):
    """Startsida med hero, om oss, tjänster och 1 featured team-medlem"""
    
    # Hero section
    hero_title = models.CharField(
        max_length=255,
        default="Din Auktoriserade Redovisningsbyrå",
        verbose_name="Hero rubrik"
    )
    hero_subtitle = RichTextField(
        blank=True,
        verbose_name="Hero undertext"
    )
    hero_cta_text = models.CharField(
        max_length=100,
        default="Kontakta oss",
        verbose_name="Knapptext"
    )
    hero_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Hero bild"
    )
    
    # Om oss-sektion
    about_title = models.CharField(
        max_length=255,
        blank=True,
        default="Om Harpans Redovisning",
        verbose_name="Om oss - Rubrik"
    )
    about_text = RichTextField(
        blank=True,
        verbose_name="Om oss - Text",
        help_text="Kort beskrivning av företaget"
    )
    
    # Värdering/USP 1
    value_1_icon = models.CharField(
        max_length=50,
        blank=True,
        default="heart",
        verbose_name="Ikon",
        help_text="Lucide-ikonnamn"
    )
    value_1_title = models.CharField(
        max_length=100,
        blank=True,
        default="Personlig service",
        verbose_name="Rubrik"
    )
    value_1_text = models.TextField(
        blank=True,
        default="Vi tror på långsiktiga relationer",
        verbose_name="Text"
    )
    
    # Värdering/USP 2
    value_2_icon = models.CharField(
        max_length=50,
        blank=True,
        default="shield-check",
        verbose_name="Ikon"
    )
    value_2_title = models.CharField(
        max_length=100,
        blank=True,
        default="Transparens",
        verbose_name="Rubrik"
    )
    value_2_text = models.TextField(
        blank=True,
        default="Inga dolda avgifter",
        verbose_name="Text"
    )
    
    # Värdering/USP 3
    value_3_icon = models.CharField(
        max_length=50,
        blank=True,
        default="zap",
        verbose_name="Ikon"
    )
    value_3_title = models.CharField(
        max_length=100,
        blank=True,
        default="Modern teknologi",
        verbose_name="Rubrik"
    )
    value_3_text = models.TextField(
        blank=True,
        default="Digitala lösningar",
        verbose_name="Text"
    )
    
    # Main content
    body = StreamField([
        ('heading', blocks.CharBlock(
            form_classname="title",
            icon='title',
            label='Rubrik'
        )),
        ('paragraph', blocks.RichTextBlock(
            label='Paragraf'
        )),
        ('image', ImageChooserBlock(
            label='Bild'
        )),
        ('services', blocks.StructBlock([
            ('title', blocks.CharBlock(label='Rubrik')),
            ('services', blocks.ListBlock(
                blocks.StructBlock([
                    ('icon', blocks.CharBlock(
                        help_text='Lucide icon namn',
                        label='Ikon'
                    )),
                    ('title', blocks.CharBlock(label='Titel')),
                    ('description', blocks.TextBlock(label='Beskrivning')),
                ])
            ))
        ], icon='list-ul', label='Tjänster')),
    ], blank=True, use_json_field=True, verbose_name="Extra innehåll (valfritt)")
    
    # Instagram
    show_instagram = models.BooleanField(
        default=True,
        verbose_name="Visa Instagram-flöde"
    )
    
    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('hero_title'),
            FieldPanel('hero_subtitle'),
            FieldPanel('hero_cta_text'),
            FieldPanel('hero_image'),
        ], heading="Hero-sektion"),
        
        MultiFieldPanel([
            FieldPanel('about_title'),
            FieldPanel('about_text'),
        ], heading="Om oss-sektion"),
        
        MultiFieldPanel([
            FieldPanel('value_1_icon'),
            FieldPanel('value_1_title'),
            FieldPanel('value_1_text'),
        ], heading="Värdering/USP 1"),
        
        MultiFieldPanel([
            FieldPanel('value_2_icon'),
            FieldPanel('value_2_title'),
            FieldPanel('value_2_text'),
        ], heading="Värdering/USP 2"),
        
        MultiFieldPanel([
            FieldPanel('value_3_icon'),
            FieldPanel('value_3_title'),
            FieldPanel('value_3_text'),
        ], heading="Värdering/USP 3"),
        
        FieldPanel('body'),
        FieldPanel('show_instagram'),
    ]
    
    def get_context(self, request):
        """Hämtar EN slumpmässig featured team-medlem"""
        context = super().get_context(request)

        # 1) Hämta navigation settings
        nav = NavigationSettings.for_request(request)
        team_page = None

        # Om team-sida är vald i settings, använd den
        if getattr(nav, "team_page", None):
            team_page = nav.team_page.specific
        else:
            # Fallback: första live TeamPage
            from team.models import TeamPage
            team_page = TeamPage.objects.live().first()

        featured_member = None

        if team_page:
            # Alla medlemmar på den valda team-sidan
            members_qs = team_page.team_members.all()

            # Försök först med de som är "available"
            available_members = [m for m in members_qs if m.availability_status == "available"]

            # Om inga är available → ta alla
            if not available_members:
                available_members = list(members_qs)

            # Slumpa en
            if available_members:
                featured_member = random.choice(available_members)

        context["featured_member"] = featured_member
        return context


# =============================================================================
# SERVICES PAGE
# =============================================================================
class ServicesPage(BasePage):
    """Tjänstesida med lista av tjänster"""

    hero_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Hero-bild',
        help_text='Stor toppbild för sidan'
    )

    intro = RichTextField(blank=True, verbose_name="Introduktion")

    services = StreamField([
        ('service', blocks.StructBlock([
            ('icon', blocks.CharBlock(help_text='Lucide-ikon, t.ex. calculator', label='Ikon')),
            ('title', blocks.CharBlock(label='Titel')),
            ('description', blocks.TextBlock(label='Beskrivning')),
            ('features', blocks.ListBlock(blocks.CharBlock(label='Funktion'), label='Funktioner/Fördelar')),
            ('price_info', blocks.CharBlock(required=False, label='Prisinformation')),
            ('cta_text', blocks.CharBlock(default='Läs mer', label='Knapptext')),
            ('cta_link', blocks.URLBlock(required=False, label='Knapp-länk')),
        ], icon='briefcase', label='Tjänst'))
    ], blank=True, use_json_field=True, verbose_name="Tjänster")

    content_panels = Page.content_panels + [
        FieldPanel('hero_image'),
        FieldPanel('intro'),
        FieldPanel('services'),
    ]

    class Meta:
        verbose_name = "Tjänstesida"        
# =============================================================================
# LEGAL PAGE (integritetspolicy, villkor osv)
# =============================================================================
class LegalPage(BasePage):
    body = RichTextField(
        blank=True,
        verbose_name="Innehåll"
    )

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]

    class Meta:
        verbose_name = "Juridisk sida"
        verbose_name_plural = "Juridiska sidor"
