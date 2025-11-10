from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
import requests
from django.core.cache import cache

from .models import ContactPage, ContactSubmission
from .forms import ContactForm


def get_client_ip(request):
    """Hämta klientens IP-adress"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@require_POST
def contact_form_submit(request):
    """HTMX endpoint för kontaktformulär"""
    
    page_id = request.POST.get('page_id')
    page = get_object_or_404(ContactPage, id=page_id)
    
    form = ContactForm(request.POST)
    
    if form.is_valid():
        submission = form.save(commit=False)
        submission.page = page
        submission.ip_address = get_client_ip(request)
        submission.save()
        
        # Skicka email till byrån
        try:
            send_mail(
                subject=f'Ny kontaktförfrågan från {submission.name}',
                message=f"""
Ny kontaktförfrågan från webbplatsen

Namn: {submission.name}
E-post: {submission.email}
Telefon: {submission.phone}
Ämne: {submission.subject}

Meddelande:
{submission.message}

---
Inskickat: {submission.submitted_at.strftime('%Y-%m-%d %H:%M')}
                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[page.email or settings.DEFAULT_FROM_EMAIL],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Email error: {e}")
        
        return JsonResponse({
            'success': True,
            'message': 'Tack för ditt meddelande! Vi återkommer så snart som möjligt.'
        })
    else:
        return JsonResponse({
            'success': False,
            'errors': form.errors
        }, status=400)


@require_GET
def instagram_feed(request):
    """HTMX endpoint för Instagram-feed"""
    
    access_token = settings.INSTAGRAM_ACCESS_TOKEN
    
    if not access_token:
        return JsonResponse({'posts': []})
    
    # Kolla cache först
    cache_key = f'instagram_feed_{access_token[:10]}'
    cached_posts = cache.get(cache_key)
    
    if cached_posts:
        return JsonResponse({'posts': cached_posts})
    
    try:
        # Instagram Graph API
        url = 'https://graph.instagram.com/me/media'
        params = {
            'fields': 'id,caption,media_type,media_url,permalink,timestamp',
            'access_token': access_token,
            'limit': 6
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        posts = data.get('data', [])
        
        # Cacha i 1 timme
        cache.set(cache_key, posts, 3600)
        
        return JsonResponse({'posts': posts})
        
    except Exception as e:
        print(f"Instagram API error: {e}")
        return JsonResponse({'posts': []})
