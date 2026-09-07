import base64
import os

from src.service import ProductListing, InfraiClient, fulfill_listing


if __name__ == "__main__":
    if not os.environ.get("INFRAI_API_KEY"):
        raise SystemExit("Set INFRAI_API_KEY before running this example")
    sample_png = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
    )
    update = fulfill_listing(ProductListing("SKU-RED-MUG", "red-mug.png", sample_png), InfraiClient())
    print(update.receipt)
    print(update.status)
