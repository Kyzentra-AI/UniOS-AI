from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from app.core.config import settings

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    token = credentials.credentials
    try:
        from app.core.supabase_api import supabase_auth_api
        
        # Verify token securely via Supabase Auth API
        # This natively handles ES256/HS256 tokens and JWKS rotation.
        user_data = await supabase_auth_api.get_user(token)
        
        user_id = user_data.get("id")
        email = user_data.get("email")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token or user not found"
            )
            
        # Extract the payload claims unverified to maintain interface compatibility
        payload = jwt.get_unverified_claims(token)
        
        app_metadata = user_data.get("app_metadata", {})
        user_metadata = user_data.get("user_metadata", {})
        role = app_metadata.get("role") or user_metadata.get("role") or "user"

        return {
            "user_id": user_id,
            "email": email,
            "role": role,
            "payload": payload
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}"
        )


class RequireRole:
    """
    Role-Based Access Control (RBAC) Dependency.
    
    Usage Example:
        @router.get("/admin-dashboard")
        async def admin_dashboard(user: dict = Depends(RequireRole(["admin"]))):
            return {"message": f"Welcome Admin {user['email']}"}
    """
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    async def __call__(self, current_user: dict = Depends(get_current_user)) -> dict:
        user_role = current_user.get("role", "user")
        if user_role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: Access requires one of the following roles: {self.allowed_roles}"
            )
from urllib.parse import urlparse

def validate_redirect_url(redirect_to: str | None, default_path: str = "") -> str:
    """
    Validates redirect_to against allowed frontend origins to prevent Open Redirect Vulnerabilities.
    Supports relative paths (e.g. '/reset-password') by prepending FRONTEND_URL.
    Raises HTTP 400 Bad Request if redirect_to points to an untrusted external origin.
    """
    if not redirect_to:
        base = settings.FRONTEND_URL.rstrip('/')
        path = default_path.lstrip('/')
        return f"{base}/{path}".rstrip('/') if path else base

    # Convert relative path to absolute frontend URL
    if redirect_to.startswith("/"):
        return f"{settings.FRONTEND_URL.rstrip('/')}{redirect_to}"

    parsed = urlparse(redirect_to)
    origin = f"{parsed.scheme}://{parsed.netloc}".lower()

    if origin not in [o.lower() for o in settings.ALLOWED_REDIRECT_ORIGINS]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Untrusted redirect URL: '{redirect_to}'. Target domain is not in the whitelist of allowed origins."
        )

    return redirect_to


