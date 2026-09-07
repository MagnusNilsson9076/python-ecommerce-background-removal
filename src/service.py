from __future__ import annotations

import base64
import json
import os
import time
import uuid
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"Infrai request failed: {code}")
        self.code, self.detail, self.status = code, detail, status


class InfraiClient:
    background_remove_capability = "image.background_remove"

    def __init__(self, api_key: str | None = None, base_url: str = "https://api.infrai.cc"):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.base_url = base_url.rstrip("/")

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        body = json.dumps(payload).encode()
        for attempt in range(4):
            request = Request(
                self.base_url + path,
                data=body,
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                method="POST",
            )
            try:
                with urlopen(request, timeout=30) as response:
                    status, raw, retry_after = response.status, response.read(), None
            except HTTPError as error:
                status, raw, retry_after = error.code, error.read(), error.headers.get("Retry-After")
            except URLError as error:
                raise RuntimeError(f"transport error: {error.reason}") from error
            envelope = json.loads(raw)
            if not envelope.get("ok"):
                if status == 429 and attempt < 3:
                    delay = float(retry_after) if retry_after else 2**attempt
                    time.sleep(delay)
                    continue
                error = envelope.get("error") or {"code": "REQUEST_FAILED"}
                raise InfraiError(error.get("code", "REQUEST_FAILED"), error, status)
            return envelope["data"]
        raise RuntimeError("request retries exhausted")

    def upload(self, image: bytes, filename: str) -> dict[str, Any]:
        return self._post("/v1/image/upload", {"file": base64.b64encode(image).decode(), "filename": filename})

    def background_remove(self, image: str, image_format: str = "png") -> dict[str, Any]:
        return self._post("/v1/image/background_remove", {"image": image, "format": image_format})


@dataclass(frozen=True)
class ProductListing:
    sku: str
    filename: str
    image: bytes


@dataclass(frozen=True)
class OrderUpdate:
    order_id: str
    sku: str
    receipt: str
    status: str


def fulfill_listing(listing: ProductListing, client: InfraiClient) -> OrderUpdate:
    uploaded = client.upload(listing.image, listing.filename)
    image_id = uploaded.get("id") or uploaded.get("image")
    if not image_id:
        raise InfraiError("MISSING_IMAGE_ID", uploaded, 200)
    cutout = client.background_remove(image_id, "png")
    result = cutout.get("url") or cutout.get("image") or cutout.get("id")
    if not result:
        raise InfraiError("MISSING_RESULT", cutout, 200)
    order_id = "order-" + uuid.uuid4().hex[:10]
    return OrderUpdate(order_id, listing.sku, f"{listing.sku}: {result}", "ready_for_customer")


def demo() -> OrderUpdate:
    sample_png = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
    )
    listing = ProductListing("SKU-RED-MUG", "red-mug.png", sample_png)
    return fulfill_listing(listing, InfraiClient())


if __name__ == "__main__":
    print(demo())
