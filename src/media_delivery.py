"""Healthtech-shaped workflow: resend a creator's stuck verification message."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .infrai_sms import InfraiSms


@dataclass(frozen=True)
class MediaAsset:
    asset_id: str
    creator_id: str
    kind: str


@dataclass(frozen=True)
class ProcessingJob:
    job_id: str
    asset_id: str
    state: str


@dataclass(frozen=True)
class CreatorDelivery:
    message_id: str
    creator_id: str
    state: str


def resend_stuck_delivery(delivery: CreatorDelivery, client: InfraiSms) -> dict[str, Any]:
    """Resend only a stuck code, then return the provider's current event state."""
    if delivery.state != "stuck":
        return {"message_id": delivery.message_id, "state": delivery.state, "resent": False}

    client.resend(delivery.message_id)
    events = client.events(delivery.message_id)
    data = events.get("data", {})
    state = data.get("status", data.get("state", "unknown"))
    return {"message_id": delivery.message_id, "state": state, "resent": True}

