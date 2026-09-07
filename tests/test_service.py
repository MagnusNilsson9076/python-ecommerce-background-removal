import json

import pytest

from src.service import InfraiClient, ProductListing, fulfill_listing


class FakeClient(InfraiClient):
    def __init__(self):
        pass

    def upload(self, image: bytes, filename: str):
        assert filename.endswith(".jpg")
        return {"id": "img_123"}

    def background_remove(self, image: str, image_format: str = "png"):
        assert image == "img_123"
        assert image_format == "png"
        return {"url": "https://cdn.example/cutout.png"}


def test_fulfillment_marks_order_ready_after_cutout():
    update = fulfill_listing(ProductListing("SKU-1", "product.jpg", b"pixels"), FakeClient())
    assert update.status == "ready_for_customer"
    assert update.sku == "SKU-1"
    assert "cutout.png" in update.receipt
