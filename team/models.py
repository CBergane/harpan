from django.db import models
from wagtail.models import Page, Orderable
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.documents.models import Document
from wagtail.documents.blocks import DocumentChooserBlock
from modelcluster.fields import ParentalKey
from core.models import BasePage


class TeamMember(Orderable):
    """Teammedlem med Calendly-länk"""
    
    page = ParentalKey('team.TeamPage', related_name='team_members')
    
    # Grundläggande info
    name = models.CharField(max_length=255, verbose_name="Namn")
    title = models.CharField(max_length=255, verbose_name="Titel/Roll")
    bio = RichTextField(blank=True, verbose_name="Biografi")
    photo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Foto"
    )
    
    # Kontaktinformation
    email = models.EmailField(blank=True, verbose_name="E-post")
    phone = models.CharField(max_length=50, blank=True, verbose_name="Telefon")
    linkedin_url = models.URLField(blank=True, verbose_name="LinkedIn URL")
    
    # Calendly-länk för bokning
    calendly_url = models.URLField(
        blank=True,
        verbose_name="Calendly-länk",
        help_text="URL till din personliga Calendly-bokningssida (t.ex. https://calendly.com/anna-harpans)"
    )
    
    # Tillgänglighetsstatus
    AVAILABILITY_CHOICES = [
        ('available', 'Tillgänglig'),
        ('limited', 'Begränsad tillgänglighet'),
        ('unavailable', 'Ej tillgänglig'),
        ('vacation', 'Semester'),
    ]
    
    availability_status = models.CharField(
        max_length=20,
        choices=AVAILABILITY_CHOICES,
        default='available',
        verbose_name="Tillgänglighetsstatus"
    )
    
    availability_note = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Statusmeddelande",
        help_text="Visar en kort text om tillgänglighet (t.ex. 'Tillbaka 15 januari')"
    )
    
    panels = [
        FieldPanel('name'),
        FieldPanel('title'),
        FieldPanel('bio'),
        FieldPanel('photo'),
        FieldPanel('email'),
        FieldPanel('phone'),
        FieldPanel('linkedin_url'),
        FieldPanel('calendly_url'),
        FieldPanel('availability_status'),
        FieldPanel('availability_note'),
    ]
    
    class Meta:
        verbose_name = "Teammedlem"
        verbose_name_plural = "Teammedlemmar"
        ordering = ['sort_order']
    
    def get_status_badge_class(self):
        """Returnerar CSS-klasser för status-badge"""
        status_classes = {
            'available': 'bg-green-100 text-green-800 border-green-200',
            'limited': 'bg-yellow-100 text-yellow-800 border-yellow-200',
            'unavailable': 'bg-red-100 text-red-800 border-red-200',
            'vacation': 'bg-blue-100 text-blue-800 border-blue-200',
        }
        return status_classes.get(self.availability_status, 'bg-gray-100 text-gray-800')
    
    def get_status_icon(self):
        """Returnerar Lucide-ikon för status"""
        status_icons = {
            'available': 'check-circle',
            'limited': 'clock',
            'unavailable': 'x-circle',
            'vacation': 'plane',
        }
        return status_icons.get(self.availability_status, 'info')
    
    def get_status_display_text(self):
        """Returnerar display-text för status"""
        return dict(self.AVAILABILITY_CHOICES).get(self.availability_status)
    
    def get_first_name(self):
        """Returnerar förnamnet (första ordet i name)"""
        return self.name.split()[0] if self.name else ""


class TeamPage(BasePage):
    """
    Team-sida med flexible about content
    
    Använd about_content för:
    - Team-intervjuer
    - Culture videos
    - Company history
    - Office tour
    - Values/Mission content
    """
    
    # Hero section
    hero_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Hero-bild"
    )
    
    hero_video = models.ForeignKey(
        Document,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Hero video",
        help_text="Optional: Video för hero-bakgrund"
    )
    
    intro = RichTextField(
        blank=True,
        verbose_name="Introduktion",
        help_text="Kort intro-text som visas under hero"
    )
    
    # About section
    about_heading = models.CharField(
        max_length=255,
        default="Om oss",
        verbose_name="Rubrik för Om oss-sektion"
    )
    
    # ===== FLEXIBLE ABOUT CONTENT =====
    about_content = StreamField([
        # Heading
        ('heading', blocks.CharBlock(
            form_classname="title",
            icon='title',
            label='Rubrik',
            help_text='Stor rubrik'
        )),
        
        # Paragraph
        ('paragraph', blocks.RichTextBlock(
            label='Text',
            help_text='Löpande text'
        )),
        
        # Image
        ('image', ImageChooserBlock(
            label='Bild',
            help_text='Lägg till bild'
        )),
        
        # Video (NYTT!)
        ('video', DocumentChooserBlock(
            label='Video',
            help_text='Team-intervju, culture video, office tour etc',
            icon='media'
        )),
        
        # Quote
        ('quote', blocks.BlockQuoteBlock(
            label='Citat',
            help_text='Blockquote/citat'
        )),
        
        # Team Highlight (advanced block)
        ('team_highlight', blocks.StructBlock([
            ('title', blocks.CharBlock(
                label='Rubrik',
                help_text='T.ex. "Våra värderingar"'
            )),
            ('text', blocks.RichTextBlock(
                label='Text'
            )),
            ('video', DocumentChooserBlock(
                required=False,
                label='Video (optional)',
                help_text='Optional video för detta highlight'
            )),
            ('image', ImageChooserBlock(
                required=False,
                label='Bild (optional)'
            )),
        ], icon='group', label='Team Highlight',
           help_text='Highlight-sektion med text + optional media')),
        
    ], blank=True, use_json_field=True, verbose_name="Om oss-innehåll",
       help_text="Flexibelt innehåll för Om oss-sektionen. Lägg till videos, text, bilder i valfri ordning!")
    
    content_panels = Page.content_panels + [
        FieldPanel('hero_image'),
        FieldPanel('hero_video'),
        FieldPanel('intro'),
        FieldPanel('about_heading'),
        FieldPanel('about_content'),  # ← NYTT: Flexibelt innehåll!
        InlinePanel('team_members', label="Teammedlemmar"),
    ]
    
    class Meta:
        verbose_name = "Om oss"