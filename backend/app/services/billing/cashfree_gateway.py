from __future__ import annotations
import base64
import hashlib
import hmac
import logging
import time
from typing import Any, Dict, Optional
import httpx
from fastapi import HTTPException, status

from app.core.config import settings

logger = logging.getLogger(__name__)


class CashfreeGateway:
    """
    Cashfree Payment Gateway integration service.
    Handles order creation, status verification, and webhook signature verification
    for both Sandbox and Production environments.
    """

    def __init__(
        self,
        env: Optional[str] = None,
        base_url: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        api_version: Optional[str] = None,
    ):
        self.env = env or settings.CASHFREE_ENV
        self.base_url = (base_url or settings.CASHFREE_PG_BASE_URL).rstrip("/")
        self.client_id = client_id or settings.CASHFREE_CLIENT_ID
        self.client_secret = client_secret or settings.CASHFREE_CLIENT_SECRET
        self.api_version = api_version or settings.CASHFREE_API_VERSION

    def _get_headers(self) -> Dict[str, str]:
        """Headers required for authenticating with Cashfree PG APIs."""
        return {
            "x-client-id": self.client_id,
            "x-client-secret": self.client_secret,
            "x-api-version": self.api_version,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def create_order(
        self,
        order_id: str,
        amount: float,
        customer_details: Dict[str, str],
        return_url: str,
        order_note: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Creates a new payment order with Cashfree.
        Returns dict containing payment_session_id, order_id, order_status, etc.
        """
        url = f"{self.base_url}/orders"
        
        # Ensure customer phone has a valid default if not provided
        phone = customer_details.get("customer_phone")
        if not phone or len(phone) < 10:
            phone = "9999999999"

        payload = {
            "order_id": order_id,
            "order_amount": round(float(amount), 2),
            "order_currency": "INR",
            "customer_details": {
                "customer_id": customer_details["customer_id"],
                "customer_email": customer_details["customer_email"],
                "customer_phone": phone,
                "customer_name": customer_details.get("customer_name", "UniOS Learner"),
            },
            "order_meta": {
                "return_url": return_url,
            },
        }
        if order_note:
            payload["order_note"] = order_note

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self._get_headers(),
                )

                if response.status_code in (200, 201):
                    data = response.json()
                    payment_session_id = data.get("payment_session_id")
                    if not payment_session_id:
                        logger.error(f"Cashfree returned success without payment_session_id: {data}")
                        raise HTTPException(
                            status_code=status.HTTP_502_BAD_GATEWAY,
                            detail="Payment gateway did not provide a payment session ID.",
                        )
                    return data

                # Handle failure response from Cashfree
                try:
                    error_data = response.json()
                    err_msg = error_data.get("message") or error_data.get("error") or response.text
                except Exception:
                    err_msg = response.text

                logger.error(
                    f"Cashfree order creation failed with status {response.status_code}: {err_msg}"
                )
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Cashfree gateway error: {err_msg}",
                )

        except httpx.RequestError as exc:
            logger.error(f"Cashfree network connection error: {str(exc)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Unable to reach Cashfree payment gateway. Please try again shortly.",
            )

    async def verify_payment(self, order_id: str) -> Dict[str, Any]:
        """
        Fetches the definitive payment state from Cashfree server-side.
        Queries /orders/{order_id} and /orders/{order_id}/payments.
        """
        order_url = f"{self.base_url}/orders/{order_id}"
        payments_url = f"{self.base_url}/orders/{order_id}/payments"

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                order_resp = await client.get(order_url, headers=self._get_headers())
                if order_resp.status_code != 200:
                    try:
                        err = order_resp.json().get("message", order_resp.text)
                    except Exception:
                        err = order_resp.text
                    logger.error(f"Failed to fetch Cashfree order {order_id}: {err}")
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail=f"Failed to fetch order details from Cashfree: {err}",
                    )

                order_data = order_resp.json()
                
                # Fetch payment attempts to extract cashfree_payment_id if paid
                payments_resp = await client.get(payments_url, headers=self._get_headers())
                cf_payment_id = None
                payment_status = None

                if payments_resp.status_code == 200:
                    payments_list = payments_resp.json()
                    if isinstance(payments_list, list) and len(payments_list) > 0:
                        # Find first SUCCESS payment or latest payment attempt
                        successful = next(
                            (p for p in payments_list if p.get("payment_status") == "SUCCESS"),
                            payments_list[-1],
                        )
                        cf_payment_id = str(successful.get("cf_payment_id", ""))
                        payment_status = successful.get("payment_status")

                return {
                    "order_id": order_data.get("order_id"),
                    "order_status": order_data.get("order_status"),  # PAID, ACTIVE, EXPIRED
                    "order_amount": order_data.get("order_amount"),
                    "order_currency": order_data.get("order_currency", "INR"),
                    "cf_payment_id": cf_payment_id,
                    "payment_status": payment_status,
                    "raw_order": order_data,
                }

        except httpx.RequestError as exc:
            logger.error(f"Cashfree network error when verifying payment {order_id}: {str(exc)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Unable to verify payment with Cashfree. Please retry shortly.",
            )

    def verify_webhook_signature(
        self,
        payload_raw_body: bytes | str,
        signature_header: Optional[str],
        timestamp_header: Optional[str],
        max_drift_seconds: int = 300,
    ) -> bool:
        """
        Cryptographically verifies the Cashfree webhook signature (HMAC-SHA256).
        Format: Base64(HMAC-SHA256(timestamp + raw_body, client_secret))
        
        Also validates that the webhook timestamp is within max_drift_seconds (replay attack defense).
        """
        if not signature_header or not timestamp_header:
            logger.warning("Webhook verification failed: missing signature or timestamp header.")
            return False

        # Replay attack protection
        try:
            ts_int = int(timestamp_header)
            # Cashfree timestamps may be in milliseconds (> 1e11) or seconds
            if ts_int > 1_000_000_000_000:
                ts_int = ts_int // 1000
            
            now_ts = int(time.time())
            if abs(now_ts - ts_int) > max_drift_seconds:
                logger.warning(
                    f"Webhook timestamp {ts_int} is outside acceptable drift window (now={now_ts})."
                )
                return False
        except (ValueError, TypeError):
            logger.warning(f"Invalid timestamp header format: {timestamp_header}")
            return False

        # Prepare signed string
        if isinstance(payload_raw_body, bytes):
            raw_str = payload_raw_body.decode("utf-8")
        else:
            raw_str = str(payload_raw_body)

        signed_content = f"{timestamp_header}{raw_str}"

        # Compute HMAC-SHA256
        computed_hash = hmac.new(
            self.client_secret.encode("utf-8"),
            signed_content.encode("utf-8"),
            hashlib.sha256,
        ).digest()
        expected_signature = base64.b64encode(computed_hash).decode("utf-8")

        is_valid = hmac.compare_digest(expected_signature, signature_header)
        if not is_valid:
            logger.warning("Webhook signature mismatch.")
        return is_valid


cashfree_gateway = CashfreeGateway()
