"""
WhatsApp OTP service via Meta Cloud API.
Falls back to console logging in dev mode (when env vars are not set).
"""
import os
import logging

logger = logging.getLogger(__name__)

WHATSAPP_PHONE_NUMBER_ID = os.environ.get('WHATSAPP_PHONE_NUMBER_ID', '')
WHATSAPP_ACCESS_TOKEN = os.environ.get('WHATSAPP_ACCESS_TOKEN', '')
WHATSAPP_OTP_TEMPLATE = os.environ.get('WHATSAPP_OTP_TEMPLATE', 'authentication_otp')


async def send_whatsapp_otp(phone: str, otp: str) -> dict:
    """
    Send a 6-digit OTP via WhatsApp using Meta Cloud API.
    In dev mode (no env vars set), prints the OTP to the console instead.
    """
    if not WHATSAPP_PHONE_NUMBER_ID or not WHATSAPP_ACCESS_TOKEN:
        # Dev fallback — print OTP so developers can test without WABA approval
        logger.info(f"[DEV OTP] Phone: {phone} | OTP: {otp}")
        print(f"[DEV OTP] Phone: {phone} | OTP: {otp}")
        return {"status": "dev_mode", "otp": otp}

    try:
        import httpx
        url = f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
        payload = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "template",
            "template": {
                "name": WHATSAPP_OTP_TEMPLATE,
                "language": {"code": "en"},
                "components": [
                    {
                        "type": "body",
                        "parameters": [{"type": "text", "text": otp}],
                    }
                ],
            },
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                url,
                json=payload,
                headers={"Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}"},
            )
        result = response.json()
        if response.status_code == 200:
            logger.info(f"WhatsApp OTP sent to {phone}")
            return {"status": "sent", "meta_response": result}
        else:
            logger.error(f"WhatsApp API error for {phone}: {result}")
            return {"status": "error", "meta_response": result}
    except Exception as e:
        logger.error(f"WhatsApp OTP send failed for {phone}: {e}")
        return {"status": "error", "reason": str(e)}
