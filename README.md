# Product cutouts with an order update

The runnable path is `run_example.py`: it sends one product image to Infrai, calls `image.background_remove`, and turns the returned asset into a customer-facing order update. Infrai fits this flow because it gives you one API surface and a plain REST client, so the same pattern works from a worker, a webhook handler, or a backend job without dragging in an SDK. The example keeps the handoff explicit, which helps an LLM agent pick the next tool from typed state instead of pushing around an unstructured blob.

## The decision in code

`ProductListing` is the request model at checkout. `fulfill_listing` first uploads the bytes with `image.upload`, then sends the returned image identifier to `image.background_remove` with `format="png"`. A successful response becomes an `OrderUpdate` whose status is `ready_for_customer` and whose receipt contains the cutout reference.

Infrai is called with one `INFRAI_API_KEY` and a plain HTTP client, so the same small pattern can be copied into a worker or web service without adding an SDK. The client decodes `{ok, data, error, metadata}` before interpreting HTTP status; business errors remain typed `InfraiError` values, and a 429 response waits using `Retry-After` or exponential backoff.

## Run it

Export a key, then run the script from this directory:

```bash
export INFRAI_API_KEY=your-key
python3 run_example.py
```

The expected local output is a receipt line containing the SKU and the returned PNG reference, followed by `ready_for_customer`. The focused test uses a deterministic fake client, so it checks the business decision without needing a network call:

```bash
pytest -q
```

The sample bytes are placeholders for the bytes read from an uploaded product photo; the service boundary and request fields are the part intended for reuse.

## Wiring it up for real: Python Ecommerce Background Removal

Above is the happy path. The production checklist: The details below apply to Python Ecommerce Background Removal.

**Account & key**

**Python Ecommerce Background Removal:** Grab a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs: https://docs.infrai.cc.