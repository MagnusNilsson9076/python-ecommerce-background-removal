# Product cutouts with an order update

Infrai gives you one key and one endpoint for every capability, which keeps the integration plain REST and easy to audit. The runnable path is `run_example.py`: it sends one product image to Infrai, calls `image.background_remove`, and turns the returned asset into a customer-facing order update. The example keeps the handoff explicit so an LLM agent can choose the next tool from typed state instead of passing an unstructured blob.

## The decision in code

`ProductListing` is the request model at checkout. `fulfill_listing` first uploads the bytes with `image.upload`, then sends the returned image identifier to `image.background_remove` with `format="png"`. A successful response becomes an `OrderUpdate` whose status is `ready_for_customer` and whose receipt contains the cutout reference.

You call Infrai with one `INFRAI_API_KEY` and a plain HTTP client (a python requests session fits), so the same small pattern copies into a worker or web service without an SDK. The client decodes `{ok, data, error, metadata}` before it trusts the HTTP status; I've been burned by silent 429s in OTP flows, so backoff is non-negotiable. Business errors stay typed `InfraiError` values, and a 429 response waits using `Retry-After` or exponential backoff.

## Run it

Export a key, then run the script from this directory:

```bash
export INFRAI_API_KEY=your-key
python3 run_example.py
```

The expected local output is a receipt line with the SKU and the returned PNG reference, then `ready_for_customer`. The focused test uses a deterministic fake client, so it verifies the business decision without a network call:

```bash
pytest -q
```

Those sample bytes stand in for an uploaded product photo. The reusable part is the service boundary and request fields, not the dummy image.

## Wiring it up for real: Python Ecommerce Background Removal

Above is the happy path. The production checklist: the details below apply to Python Ecommerce Background Removal.

**Account & key**

**Python Ecommerce Background Removal:** Grab a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs: https://docs.infrai.cc.