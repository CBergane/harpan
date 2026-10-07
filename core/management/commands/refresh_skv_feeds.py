from django.core.management.base import BaseCommand

from core.models import AktuelltPage
from core.services.skv_rss import get_rss_items


class Command(BaseCommand):
    help = "Refreshar Skatteverkets RSS-cache för Aktuellt-sidor."

    def handle(self, *args, **options):
        pages = AktuelltPage.objects.live()

        feed_count = 0

        for page in pages:
            self.stdout.write(f"Page: {page.title}")

            for block in page.feeds:
                if block.block_type != "feed":
                    continue

                value = block.value

                title = value.get("title") or "Flöde"
                url = value["feed_url"]
                limit = value.get("max_items") or 12

                items = get_rss_items(
                    url,
                    limit,
                    force_refresh=True,
                )

                feed_count += 1

                self.stdout.write(
                    f"  {title}: {len(items)} poster"
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"RSS refresh klar: {feed_count} flöden."
            )
        )
