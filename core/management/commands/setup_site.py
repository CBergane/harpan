from django.core.management.base import BaseCommand
from wagtail.models import Page, Site
from core.models import HomePage
from team.models import TeamPage
from blog.models import BlogIndexPage
from contact.models import ContactPage


class Command(BaseCommand):
    help = 'Setup initial pages for Harpans website'

    def handle(self, *args, **options):
        # Hitta root page (ID kan variera)
        root_page = Page.objects.filter(depth=2).first()
        
        if not root_page:
            self.stdout.write(self.style.ERROR('No root page found!'))
            self.stdout.write(self.style.WARNING('Run: python manage.py wagtail_update_index'))
            return
        
        # Ta bort default welcome page
        Page.objects.filter(slug='welcome-to-your-new-wagtail-site').delete()
        
        # Skapa HomePage
        if not HomePage.objects.filter(slug='home').exists():
            home = HomePage(
                title='Hem',
                slug='home',
                hero_title='Din Auktoriserade Redovisningsbyrå',
                hero_subtitle='<p>Vi gör redovisningen enkel så att du kan fokusera på ditt företag</p>',
                hero_cta_text='Kontakta oss',
                show_instagram=False,
            )
            root_page.add_child(instance=home)
            home.save_revision().publish()
            
            # Sätt som default site homepage
            site = Site.objects.get(is_default_site=True)
            site.root_page = home
            site.save()
            
            self.stdout.write(self.style.SUCCESS('✓ Created HomePage'))
        else:
            home = HomePage.objects.first()
        
        # Skapa TeamPage
        if home and not TeamPage.objects.filter(slug='om-oss').exists():
            team_page = TeamPage(
                title='Om oss',
                slug='om-oss',
                intro='<p>Vi är ett glatt gäng med bred utbildning och värdefull erfarenhet.</p>'
            )
            home.add_child(instance=team_page)
            team_page.save_revision().publish()
            self.stdout.write(self.style.SUCCESS('✓ Created TeamPage'))
        
        # Skapa BlogIndexPage
        if home and not BlogIndexPage.objects.filter(slug='blogg').exists():
            blog = BlogIndexPage(
                title='Blogg',
                slug='blogg',
                intro='<p>Nyheter, tips och råd om redovisning och företagande</p>'
            )
            home.add_child(instance=blog)
            blog.save_revision().publish()
            self.stdout.write(self.style.SUCCESS('✓ Created BlogIndexPage'))
        
        # Skapa ContactPage
        if home and not ContactPage.objects.filter(slug='kontakt').exists():
            contact = ContactPage(
                title='Kontakt',
                slug='kontakt',
                intro='<p>Välkommen att kontakta oss! Vi svarar så snart vi kan.</p>',
                address='Stockholm, Sverige',
                phone='08-XXX XX XX',
                email='info@harpans.se',
                opening_hours='<p>Mån-Fre: 08:00-17:00</p>'
            )
            home.add_child(instance=contact)
            contact.save_revision().publish()
            self.stdout.write(self.style.SUCCESS('✓ Created ContactPage'))
        
        self.stdout.write(self.style.SUCCESS('\n🎉 Site setup complete!'))
        self.stdout.write(self.style.SUCCESS('Visit: http://127.0.0.1:8000/'))