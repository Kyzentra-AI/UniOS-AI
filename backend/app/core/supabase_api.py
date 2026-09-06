import httpx
from app.core.config import settings

class SupabaseAuthAPI:
    """
    Asynchronous helper class to interact directly with Supabase GoTrue API.
    This guarantees thread-safety and avoids session mutation issues of the SDK.
    """
    
    @staticmethod
    def _get_headers(token: str | None = None) -> dict:
        headers = {
            "apikey": settings.SUPABASE_ANON_KEY,
            "Content-Type": "application/json"
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    async def sign_up(self, email: str, password: str, full_name: str, terms_accepted: bool, redirect_to: str | None = None) -> dict:
        url = f"{settings.SUPABASE_URL}/auth/v1/signup"
        options = {
            "data": {
                "full_name": full_name,
                "terms_accepted": terms_accepted
            }
        }
        if redirect_to:
            options["email_redirect_to"] = redirect_to

        body = {
            "email": email,
            "password": password,
            "options": options
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=body, headers=self._get_headers())
            if response.status_code != 200:
                raise Exception(response.json().get("msg", "Signup failed"))
            return response.json()

    async def verify_otp(self, email: str, token: str, type: str = "signup") -> dict:
        url = f"{settings.SUPABASE_URL}/auth/v1/verify"
        body = {
            "email": email,
            "token": token,
            "type": type
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=body, headers=self._get_headers())
            if response.status_code != 200:
                raise Exception(response.json().get("msg", "OTP verification failed"))
    async def resend_verification(self, email: str, redirect_to: str | None = None) -> dict:
        url = f"{settings.SUPABASE_URL}/auth/v1/resend"
        options = {}
        if redirect_to:
            options["email_redirect_to"] = redirect_to

        body = {
            "email": email,
            "type": "signup"
        }
        if options:
            body["options"] = options

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=body, headers=self._get_headers())
            if response.status_code != 200:
                raise Exception(response.json().get("msg", response.json().get("error_description", "Resend verification failed")))
            return response.json()

    async def sign_in(self, email: str, password: str) -> dict:

        url = f"{settings.SUPABASE_URL}/auth/v1/token?grant_type=password"
        body = {
            "email": email,
            "password": password
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=body, headers=self._get_headers())
            if response.status_code != 200:
                raise Exception(response.json().get("error_description", "Invalid login credentials"))
            return response.json()

    async def forgot_password(self, email: str, redirect_to: str | None = None) -> dict:
        url = f"{settings.SUPABASE_URL}/auth/v1/recover"
        if redirect_to:
            url += f"?redirect_to={httpx.QueryParams({'redirect_to': redirect_to}).get('redirect_to')}"
        body = {
            "email": email
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=body, headers=self._get_headers())
            if response.status_code != 200:
                raise Exception(response.json().get("msg", "Password recovery initiation failed"))
            return response.json()

    async def update_password(self, token: str, new_password: str) -> dict:
        url = f"{settings.SUPABASE_URL}/auth/v1/user"
        body = {
            "password": new_password
        }
        async with httpx.AsyncClient() as client:
            response = await client.put(url, json=body, headers=self._get_headers(token))
            if response.status_code != 200:
                raise Exception(response.json().get("msg", "Password reset failed"))
            return response.json()

    async def logout(self, token: str) -> None:
        url = f"{settings.SUPABASE_URL}/auth/v1/logout"
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self._get_headers(token))
            if response.status_code not in (200, 204):
                raise Exception(response.json().get("msg", "Logout failed"))

    # Multi-Factor Authentication GoTrue HTTP calls
    async def mfa_enroll(self, token: str) -> dict:
        url = f"{settings.SUPABASE_URL}/auth/v1/factors"
        body = {
            "factor_type": "totp",
            "friendly_name": "UniOS Authenticator"
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=body, headers=self._get_headers(token))
            try:
                data = response.json()
            except Exception:
                data = {"msg": response.text}
            
            if response.status_code not in (200, 201):
                raise Exception(data.get("msg", data.get("error_description", f"MFA enrollment failed: {response.status_code} {response.text}")))
            return data

    async def mfa_challenge(self, token: str, factor_id: str) -> dict:
        url = f"{settings.SUPABASE_URL}/auth/v1/factors/{factor_id}/challenge"
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self._get_headers(token))
            if response.status_code != 200:
                raise Exception(response.json().get("msg", "MFA challenge failed"))
            return response.json()

    async def mfa_verify(self, token: str, factor_id: str, challenge_id: str, code: str) -> dict:
        url = f"{settings.SUPABASE_URL}/auth/v1/factors/{factor_id}/verify"
        body = {
            "challenge_id": challenge_id,
            "code": code
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=body, headers=self._get_headers(token))
            if response.status_code != 200:
                raise Exception(response.json().get("msg", "MFA verification failed"))
            return response.json()

    async def mfa_unenroll(self, token: str, factor_id: str) -> dict:
        url = f"{settings.SUPABASE_URL}/auth/v1/factors/{factor_id}"
        async with httpx.AsyncClient() as client:
            response = await client.delete(url, headers=self._get_headers(token))
            if response.status_code != 200:
                raise Exception(response.json().get("msg", "MFA unenroll failed"))
            return response.json()

    async def exchange_code_for_session(self, auth_code: str, code_verifier: str | None = None) -> dict:
        url = f"{settings.SUPABASE_URL}/auth/v1/token?grant_type=pkce_code"
        body = {
            "auth_code": auth_code
        }
        if code_verifier:
            body["code_verifier"] = code_verifier

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=body, headers=self._get_headers())
            if response.status_code != 200:
                raise Exception(response.json().get("error_description", response.json().get("msg", "Code exchange failed")))
            return response.json()

    async def refresh_token(self, refresh_token: str) -> dict:
        url = f"{settings.SUPABASE_URL}/auth/v1/token?grant_type=refresh_token"
        body = {
            "refresh_token": refresh_token
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=body, headers=self._get_headers())
            if response.status_code != 200:
                raise Exception(response.json().get("error_description", response.json().get("msg", "Token refresh failed")))
            return response.json()

supabase_auth_api = SupabaseAuthAPI()
