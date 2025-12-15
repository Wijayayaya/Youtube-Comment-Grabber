from __future__ import annotations

import logging
from typing import Optional

from obswebsocket import obsws, requests as obs_requests

logger = logging.getLogger(__name__)


def send_text_to_obs(host: str, port: int, password: str | None, source: str, text: str) -> bool:
    """Connect to OBS WebSocket and set the text of a source.

    Returns True on success, False otherwise.
    """
    try:
        ws = obsws(host, port, password or "")
        ws.connect()
        # Try common request for text sources. obs-websocket v4 uses SetTextGDIPlusProperties
        try:
            ws.call(obs_requests.SetTextGDIPlusProperties(source=source, text=text))
        except Exception:
            # Fallback to SetTextFreetype2Properties for other text source types
            try:
                ws.call(obs_requests.SetTextFreetype2Properties(source=source, text=text))
            except Exception as exc:
                logger.exception("Failed to set text on OBS source %s: %s", source, exc)
                ws.disconnect()
                return False
        ws.disconnect()
        return True
    except Exception as exc:
        logger.exception("OBS connection/send failed: %s", exc)
        return False
