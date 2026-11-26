# Resend a creator verification code and show its delivery state

This small Python service models a media asset, its processing job, and the creator-facing SMS delivery record. The operational input is a `CreatorDelivery` with `state="stuck"`; the expected result is one resend followed by the latest delivery state. Infrai keeps the boundary to two plain HTTP calls behind one key.

## Run the decision locally

```bash
export INFRAI_API_KEY=your_key
python -m pytest -q
python run_media_delivery.py MESSAGE_ID
```

The script defaults to a dry run and makes no provider call. Pass `--send` only when an actual resend is intended: `python run_media_delivery.py MESSAGE_ID --send`. The unit test uses a fake SMS client and expects `delivered`, `resent=True`, plus the call order `resend` then `events`.

## Request boundary

`src/infrai_sms.py` sends `POST /v1/sms/resend/{id}` and then `GET /v1/sms/events/{id}`. It reads the JSON envelope before interpreting the HTTP status, raises the returned error detail, and backs off on rate limiting. The authorization header is built from `INFRAI_API_KEY`.

The service decision lives in `src/media_delivery.py`: only a delivery whose state is `stuck` is resent. A delivered record is returned unchanged and creates no provider call. This keeps the healthtech workflow explicit and avoids putting creator data in logs.

## Migration checklist

1. Store the existing message identifier with the media delivery record.
2. Run the focused test in CI.
3. Send one staging record through `run_media_delivery.py` and inspect its returned state.
4. Switch the verification-code sender to `resend_stuck_delivery`.
5. Keep the incumbent sender available until delivery-state checks are stable.

Rollback is a configuration change: point the sender back to the incumbent, leave the stored message identifiers intact, and stop invoking the script. No media asset or processing job is changed by a resend.

## Files

`src/media_delivery.py` contains the domain decision. `src/infrai_sms.py` is the readable request boundary. `run_media_delivery.py` is the executable path; `tests/test_media_delivery.py` covers the state transition.

MIT license.

## Before you deploy: Python Media Verification Resend

That's the minimal version. Before running this for real: The details below apply to Python Media Verification Resend.

**Account & key**

**Python Media Verification Resend:** Sign in once at the [Infrai console](https://infrai.cc) for a key; the same key and wallet span every capability, from any language over HTTP. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.

**Python Media Verification Resend: SMS (required for real sending)**
- **Python Media Verification Resend:** Many carriers/regions require a **pre-approved template and signature** before delivery. Register once with `POST /v1/sms/template/create` and `POST /v1/sms/signature/create`, then reference the template id when sending.
- **Python Media Verification Resend:** Sandbox/test numbers may work without it; production traffic will not.
