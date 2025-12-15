from __future__ import annotations

import time

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from comments.models import LiveStream
from comments.services.ingest import store_live_chat_items
from comments.services.youtube import (
    build_youtube_service,
    fetch_live_chat_page,
    get_live_chat_metadata,
)


class Command(BaseCommand):
    help = "Ambil live chat dari streaming aktif dan simpan ke database."

    def add_arguments(self, parser):
        parser.add_argument("--video-id", required=True, help="ID video live YouTube")
        parser.add_argument(
            "--loop",
            action="store_true",
            help="Tetap mem-polling sampai dihentikan (Ctrl+C)",
        )
        parser.add_argument(
            "--max-iterations",
            type=int,
            default=0,
            help="Batasi jumlah iterasi saat loop berjalan (0 = tanpa batas)",
        )

    def handle(self, *args, **options):
        video_id = options["video_id"]
        youtube = build_youtube_service()
        metadata = get_live_chat_metadata(youtube, video_id)
        if not metadata or not metadata.get("live_chat_id"):
            raise CommandError("Live chat tidak ditemukan atau belum aktif untuk video tersebut.")

        live_stream, _ = LiveStream.objects.get_or_create(
            video_id=video_id,
            defaults={"title": metadata.get("title") or video_id},
        )
        if metadata.get("title") and live_stream.title != metadata["title"]:
            live_stream.title = metadata["title"]
            live_stream.save(update_fields=["title", "updated_at"])

        live_stream.last_live_chat_id = metadata["live_chat_id"]
        live_stream.save(update_fields=["last_live_chat_id", "updated_at"])

        self.stdout.write(self.style.NOTICE(f"Mulai menarik live chat untuk {live_stream}"))

        loop = options["loop"]
        max_iterations = options["max_iterations"]
        iterations = 0
        page_token = None

        try:
            while True:
                items, page_token, wait_ms = fetch_live_chat_page(
                    youtube, metadata["live_chat_id"], page_token
                )
                new_count = store_live_chat_items(live_stream, items)
                if new_count:
                    self.stdout.write(self.style.SUCCESS(f"Tersimpan {new_count} pesan baru"))
                else:
                    self.stdout.write("Belum ada pesan baru")

                live_stream.last_polled_at = timezone.now()
                live_stream.save(update_fields=["last_polled_at", "updated_at"])

                iterations += 1
                if not loop:
                    break
                if max_iterations and iterations >= max_iterations:
                    break
                # Use a fixed 180 seconds sleep to reduce polling frequency
                time.sleep(180)
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("Polling dihentikan oleh pengguna"))
