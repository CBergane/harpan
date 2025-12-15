from datetime import timedelta

import requests
from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST, require_GET

from .forms import ContactForm
from .models import ContactPage, ContactSubmission


# --- Konfiguration för rate limiting ---
MAX_CONTACT_ATTEMPTS = 2            # Kontaktformulär: max 2 försök
CONTACT_WINDOW_MINUTES = 30         # per 30 minuter

CALLBACK_MAX_ATTEMPTS = 2           # Callback: max 2 försök
CALLBACK_WINDOW_MINUTES = 45        # per 45 minuter


def get_client_ip(request):
    """Hämta klientens IP-adress (tar hänsyn till proxy/X-Forwarded-For)."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip or "0.0.0.0"


# -------------------------------------------------------------------
#  KONTAKTFORMULÄR (”Skicka meddelande”)
# -------------------------------------------------------------------
@require_POST
def contact_form_submit(request):
    """
    HTMX endpoint för kontaktformuläret.
    - Honeypot (fält "website") för bottar.
    - Rate limit per IP med DB (ContactSubmission).
    - Skickar snyggt mail till byråns adress.
    """
    # 🕵️ Honeypot – om detta fält är ifyllt är det nästan säkert en bot
    honeypot = (request.POST.get("website") or "").strip()
    if honeypot:
        return JsonResponse({
            "success": True,
            "message": "Tack! Vi har mottagit din förfrågan."
        })

    page_id = request.POST.get("page_id")
    page = get_object_or_404(ContactPage, id=page_id)

    ip = get_client_ip(request)

    # 🔹 Rate limit: max N submissions per IP under senaste X minuter
    cutoff = timezone.now() - timedelta(minutes=CONTACT_WINDOW_MINUTES)
    recent_count = ContactSubmission.objects.filter(
        ip_address=ip,
        submitted_at__gte=cutoff,
    ).count()

    if recent_count >= MAX_CONTACT_ATTEMPTS:
        # Vi svarar snällt, men sparar inget och skickar inget mail
        return JsonResponse({
            "success": True,
            "message": "Tack! Vi har redan mottagit din förfrågan. "
                       "För att undvika spam kan du skicka igen om en liten stund."
        })

    form = ContactForm(request.POST)

    if form.is_valid():
        submission = form.save(commit=False)
        submission.page = page
        submission.ip_address = ip
        submission.save()

        # Skicka email till byrån
        try:
            org_line = submission.org_number or "Ej angivet"
            phone_line = submission.phone or "Ej angivet"
            subject_line = submission.subject or "Ej angivet"

            message = f"""
Ny kontaktförfrågan från webbplatsen

----------------------------------------
   Kunduppgifter
----------------------------------------
Namn:             {submission.name}
Organisationsnr:  {org_line}
E-post:           {submission.email}
Telefon:          {phone_line}
Ämne:             {subject_line}

----------------------------------------
   Meddelande
----------------------------------------
{submission.message}

----------------------------------------
   Tekniskt
----------------------------------------
Inskickat: {submission.submitted_at:%Y-%m-%d %H:%M}
IP-adress: {submission.ip_address or "Okänd"}
Sida:      {page.title}
            """.strip()

            send_mail(
                subject=f"Ny kontaktförfrågan från {submission.name}",
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[page.email or settings.DEFAULT_FROM_EMAIL],
                fail_silently=False,
            )
        except Exception as e:
            # Logga ev. i framtiden
            print(f"Email error (contact_form_submit): {e}")

        return JsonResponse({
            "success": True,
            "message": "Tack för ditt meddelande! Vi återkommer så snart som möjligt."
        })

    # Formuläret var ogiltigt – skicka tillbaka valideringsfel
    return JsonResponse({
        "success": False,
        "errors": form.errors,
    }, status=400)


# -------------------------------------------------------------------
#  CALLBACK (”Vi ringer upp dig”)
# -------------------------------------------------------------------
@require_POST
def callback_request(request):
    """
    HTMX-endpoint för 'Vi ringer upp dig'-formuläret.
    - Honeypot (fält "website") för bottar.
    - Rate limit per IP med cache.
    - Skickar ett kort mail till byrån.
    """

    # 🕵️ Honeypot igen
    honeypot = (request.POST.get("website") or "").strip()
    if honeypot:
        html = """
        <div class="bg-green-50 border border-green-200 text-green-800 px-4 py-3 rounded-lg text-sm animate-fade-in">
          <p><strong>Tack!</strong> Din förfrågan är mottagen.</p>
        </div>
        """
        return HttpResponse(html)

    ip = get_client_ip(request)
    cache_key = f"callback_rate_{ip}"
    current = cache.get(cache_key, 0)

    WINDOW_SECONDS = CALLBACK_WINDOW_MINUTES * 60

    if current >= CALLBACK_MAX_ATTEMPTS:
        throttled_html = """
        <div class="bg-green-50 border border-green-200 text-green-800 px-4 py-3 rounded-lg text-sm animate-fade-in">
          <p><strong>Tack!</strong> Vi har redan mottagit din förfrågan. 
          Om du inte hört något inom kort, ring oss gärna.</p>
        </div>
        """
        return HttpResponse(throttled_html)

    # Uppdatera räknaren i cache
    if current == 0:
        cache.set(cache_key, 1, WINDOW_SECONDS)
    else:
        try:
            cache.incr(cache_key)
        except ValueError:
            cache.set(cache_key, 1, WINDOW_SECONDS)

    name = (request.POST.get("name") or "").strip()
    phone = (request.POST.get("phone") or "").strip()
    email = (request.POST.get("email") or "").strip()
    preferred_time = (request.POST.get("preferred_time") or "").strip()
    message = (request.POST.get("message") or "").strip()
    page_id = request.POST.get("page_id")

    if not name or not phone:
        html = """
        <div class="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg text-sm error-shake">
          <p><strong>Fel:</strong> Fyll i både namn och telefonnummer.</p>
        </div>
        """
        return HttpResponse(html, status=400)

    # Hämta ContactPage om vi har page_id
    page = None
    if page_id:
        try:
            page = ContactPage.objects.get(id=page_id)
        except ContactPage.DoesNotExist:
            page = None

    if page and page.email:
        recipient = page.email
    else:
        recipient = settings.DEFAULT_FROM_EMAIL

    preferred_map = {
        "morning": "Förmiddag (08:00–12:00)",
        "afternoon": "Eftermiddag (12:00–17:00)",
        "anytime": "När som helst under dagen",
    }
    preferred_label = preferred_map.get(preferred_time, "Ej angivet")

    body_lines = [
        "Ny uppringningsförfrågan från webbplatsen",
        "",
        f"Namn: {name}",
        f"Telefon: {phone}",
    ]
    if email:
        body_lines.append(f"E-post: {email}")
    if preferred_time:
        body_lines.append(f"Bästa tid att ringa: {preferred_label}")
    if message:
        body_lines.append("")
        body_lines.append("Meddelande:")
        body_lines.append(message)

    body_lines.append("")
    body_lines.append(f"IP-adress: {get_client_ip(request)}")

    mail_body = "\n".join(body_lines)

    try:
        result = send_mail(
            subject=f"Uppringningsförfrågan från {name}",
            message=mail_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            fail_silently=False,
        )
        print("send_mail result (callback_request):", result)

        success_html = """
        <div class="bg-green-50 border border-green-200 text-green-800 px-4 py-3 rounded-lg text-sm animate-fade-in">
          <p><strong>Tack!</strong> Din förfrågan är mottagen. Vi ringer upp dig så snart vi kan.</p>
        </div>
        """
        return HttpResponse(success_html)
    except Exception as e:
        print("Callback email error:", repr(e))
        error_html = """
        <div class="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg text-sm animate-fade-in">
          <p><strong>Oj!</strong> Något gick fel när vi skulle skicka din förfrågan. 
          Försök igen eller ring oss direkt.</p>
        </div>
        """
        return HttpResponse(error_html, status=500)


# -------------------------------------------------------------------
#  INSTAGRAM-FEED
# -------------------------------------------------------------------
@require_GET
def instagram_feed(request):
    """HTMX endpoint för Instagram-feed."""
    access_token = settings.INSTAGRAM_ACCESS_TOKEN

    if not access_token:
        return JsonResponse({"posts": []})

    cache_key = f"instagram_feed_{access_token[:10]}"
    cached_posts = cache.get(cache_key)

    if cached_posts:
        return JsonResponse({"posts": cached_posts})

    try:
        url = "https://graph.instagram.com/me/media"
        params = {
            "fields": "id,caption,media_type,media_url,permalink,timestamp",
            "access_token": access_token,
            "limit": 6,
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        posts = data.get("data", [])

        # Cacha i 1 timme
        cache.set(cache_key, posts, 3600)

        return JsonResponse({"posts": posts})

    except Exception as e:
        print(f"Instagram API error: {e}")
        return JsonResponse({"posts": []})
