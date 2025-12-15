# blog/views.py
from django.views.decorators.http import require_POST
from django.http import HttpResponse, JsonResponse
from django.utils.html import escape

from .models import BlogSubscriber


@require_POST
def blog_subscribe(request):
    """
    Tar emot email från formuläret och lägger till/aktiverar prenumerant.
    Returnerar en liten HTML-snutt (HTMX-vänlig).
    """
    email = (request.POST.get("email") or "").strip().lower()
    honeypot = (request.POST.get("website") or "").strip()

    # Honeypot: bottar fyller ofta i detta fält
    if honeypot:
        # svara "success" men gör inget
        html = """
        <div class="bg-green-50 border border-green-200 text-green-800 px-4 py-3 rounded-lg text-sm">
          <p>Tack! Om din adress är giltig kommer du få framtida uppdateringar.</p>
        </div>
        """
        return HttpResponse(html)

    if not email:
        html = """
        <div class="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg text-sm">
          <p>Fyll i en giltig e-postadress.</p>
        </div>
        """
        return HttpResponse(html, status=400)

    sub, created = BlogSubscriber.objects.get_or_create(email=email)

    if not created and not sub.active:
        sub.active = True
        sub.save(update_fields=["active"])

    msg = escape(email)

    html = f"""
    <div class="bg-green-50 border border-green-200 text-green-800 px-4 py-3 rounded-lg text-sm animate-fade-in">
      <p><strong>Tack!</strong> {msg} är nu anmäld för uppdateringar. Du får ett mail nästa gång vi publicerar nytt innehåll.</p>
    </div>
    """
    return HttpResponse(html)


def blog_unsubscribe(request, token):
    """
    Enkel avanmälan via unik token i länken.
    """
    from django.shortcuts import get_object_or_404, render
    from .models import BlogSubscriber

    subscriber = get_object_or_404(BlogSubscriber, unsubscribe_token=token)

    if subscriber.active:
        subscriber.active = False
        subscriber.save(update_fields=["active"])

    return render(request, "blog/unsubscribe_done.html", {"subscriber": subscriber})
