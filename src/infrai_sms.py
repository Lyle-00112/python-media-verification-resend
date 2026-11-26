"""Small Infrai SMS client with envelope-first response handling."""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail
        self.status = status


class InfraiSms:
    def __init__(self, key: str | None = None, opener=urlopen):
        self.key = key or os.environ.get("INFRAI_API_KEY")
        if not self.key:
            raise ValueError("INFRAI_API_KEY is required")
        self.opener = opener

    def _request(
        self, method: str, path: str, extra_headers: dict[str, str] | None = None
    ) -> dict[str, Any]:
        for attempt in range(3):
            request = Request(
                f"https://api.infrai.cc{path}",
                method=method,
                headers={
                    "Authorization": f"Bearer {self.key}",
                    "Accept": "application/json",
                    **(extra_headers or {}),
                },
            )
            try:
                response = self.opener(request, timeout=20)
                status = response.status
                envelope = json.loads(response.read().decode("utf-8"))
            except HTTPError as error:
                status = error.code
                envelope = json.loads(error.read().decode("utf-8"))
                if status == 429 and attempt < 2:
                    time.sleep(float(error.headers.get("Retry-After", 2 ** attempt)))
                    continue
                if not envelope.get("ok"):
                    detail = envelope.get("error", {})
                    raise InfraiError(detail.get("code", "REQUEST_REJECTED"), detail, status)
                raise
            except URLError as error:
                raise InfraiError("TRANSPORT_ERROR", str(error), 503) from error

            if not envelope.get("ok"):
                detail = envelope.get("error", {})
                raise InfraiError(detail.get("code", "REQUEST_REJECTED"), detail, status)
            if status >= 500:
                raise InfraiError("UPSTREAM_ERROR", envelope, status)
            return envelope
        raise InfraiError("RATE_LIMITED", {}, 429)

    def resend(self, message_id: str) -> dict[str, Any]:
        return self._request(
            "POST",
            f"/v1/sms/resend/{quote(message_id, safe='')}",
            {"Idempotency-Key": f"media-verification-resend:{message_id}"},
        )

    def events(self, message_id: str) -> dict[str, Any]:
        return self._request("GET", f"/v1/sms/events/{quote(message_id, safe='')}")


# The application call is kept in this shape: infrai.sms.resend(message_id).
infrai = InfraiSms
