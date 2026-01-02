from __future__ import annotations

import time

from django.core.management.base import BaseCommand
from django.utils import timezone

from comments.models import LiveStream
from comments.services.ingest import store_live_chat_items
from comments.services.youtube import (
	build_youtube_service,
	fetch_live_chat_page,
	get_live_chat_metadata,
)


class Command(BaseCommand):
	help = "Polling seluruh LiveStream aktif yang terdaftar di admin."

	def add_arguments(self, parser):
		parser.add_argument(
			"--video-id",
			action="append",
			dest="video_ids",
			help="Batasi hanya ke video tertentu (gunakan berulang untuk lebih dari satu)",
		)
		parser.add_argument(
			"--loop",
			action="store_true",
			help="Teruskan polling sampai dihentikan",
		)
		parser.add_argument(
			"--interval",
			type=int,
			default=300,
			help="Jeda antar siklus (detik) saat --loop aktif",
		)
		parser.add_argument(
			"--refresh-metadata",
			action="store_true",
			help="Perbarui metadata video di setiap siklus",
		)

	def handle(self, *args, **options):
		video_ids = options["video_ids"] or []
		youtube = build_youtube_service()
		metadata_cache: dict[int, str] = {}

		loop = options["loop"]
		interval = max(1, options["interval"])
		refresh_metadata = options["refresh_metadata"]

		try:
			while True:
				# Re-query streams setiap cycle agar bisa detect stream baru
				streams_qs = LiveStream.objects.filter(is_active=True)
				if video_ids:
					streams_qs = streams_qs.filter(video_id__in=video_ids)
				streams = list(streams_qs)
				
				if not streams:
					self.stdout.write(self.style.WARNING("Tidak ada LiveStream aktif yang bisa diproses."))
					if not loop:
						return
					self.stdout.write(self.style.NOTICE(f"Menunggu {interval}s sebelum cek lagi..."))
					time.sleep(interval)
					continue

				self.stdout.write(
					self.style.NOTICE(
						f"Memproses {len(streams)} stream: {', '.join(stream.video_id for stream in streams)}"
					)
				)

				cycle_saved = 0
				for stream in streams:
					live_chat_id = metadata_cache.get(stream.id)
					if refresh_metadata or not live_chat_id:
						metadata = get_live_chat_metadata(youtube, stream.video_id)
						if not metadata or not metadata.get("live_chat_id"):
							self.stdout.write(
								self.style.WARNING(
									f"Live chat belum aktif untuk {stream.video_id}"
								)
							)
							continue
						live_chat_id = metadata["live_chat_id"]
						metadata_cache[stream.id] = live_chat_id
						if metadata.get("title") and stream.title != metadata["title"]:
							stream.title = metadata["title"]
						stream.last_live_chat_id = live_chat_id

					page_token = stream.next_page_token or None
					try:
						items, next_token, _ = fetch_live_chat_page(
							youtube, live_chat_id, page_token
						)
						new_count = store_live_chat_items(stream, items)
						cycle_saved += new_count
						stream.next_page_token = next_token or ""
						stream.last_polled_at = timezone.now()
						stream.save(
							update_fields=[
								"title",
								"last_live_chat_id",
								"next_page_token",
								"last_polled_at",
								"updated_at",
							]
						)
						if new_count:
							self.stdout.write(
								self.style.SUCCESS(f"{stream.video_id}: {new_count} pesan baru")
							)
					except Exception as exc:
						self.stderr.write(f"Gagal memproses {stream.video_id}: {exc}")

				if not loop:
					break
				if cycle_saved == 0:
					self.stdout.write(
						self.style.NOTICE(f"Tidak ada pesan baru, tidur {interval}s sebelum siklus berikutnya")
					)
				time.sleep(interval)
		except KeyboardInterrupt:
			self.stdout.write(self.style.WARNING("Polling dihentikan oleh pengguna"))
