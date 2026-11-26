import logging
import uuid
from typing import List, Optional
from app.core.supabase import supabase_admin

logger = logging.getLogger(__name__)


class StorageService:
    BUCKET_NAME = "syllabi"
    AVATARS_BUCKET = "avatars"

    @classmethod
    def upload_file(cls, file_bytes: bytes, file_name: str, content_type: str = "application/pdf") -> str:
        file_ext = file_name.split(".")[-1] if "." in file_name else "pdf"
        unique_name = f"{uuid.uuid4()}.{file_ext}"
        storage_key = f"uploads/{unique_name}"

        supabase_admin.storage.from_(cls.BUCKET_NAME).upload(
            path=storage_key,
            file=file_bytes,
            file_options={"content-type": content_type},
        )
        return storage_key

    @classmethod
    def upload_avatar(cls, user_id: str, file_bytes: bytes, file_ext: str, content_type: str) -> tuple[str, str]:
        """Uploads a profile avatar and returns (storage_key, public_url)."""
        unique_name = f"{user_id}/{uuid.uuid4()}.{file_ext}"
        try:
            supabase_admin.storage.from_(cls.AVATARS_BUCKET).upload(
                path=unique_name,
                file=file_bytes,
                file_options={"content-type": content_type},
            )
            public_url = supabase_admin.storage.from_(cls.AVATARS_BUCKET).get_public_url(unique_name)
            return f"{cls.AVATARS_BUCKET}/{unique_name}", str(public_url)
        except Exception:
            # Fallback to syllabi bucket under avatars/ prefix if dedicated bucket is unavailable
            fallback_key = f"avatars/{unique_name}"
            supabase_admin.storage.from_(cls.BUCKET_NAME).upload(
                path=fallback_key,
                file=file_bytes,
                file_options={"content-type": content_type},
            )
            public_url = supabase_admin.storage.from_(cls.BUCKET_NAME).get_public_url(fallback_key)
            return fallback_key, str(public_url)

    @classmethod
    def create_signed_url(cls, bucket_name: Optional[str], storage_key: str, expires_in: int = 300) -> str:
        """Generates a short-lived signed download URL for a Supabase Storage object."""
        bucket = bucket_name or cls.BUCKET_NAME
        res = supabase_admin.storage.from_(bucket).create_signed_url(storage_key, expires_in)
        if isinstance(res, dict):
            return res.get("signedURL") or res.get("signedUrl") or res.get("signed_url") or ""
        return str(res or "")

    @classmethod
    def delete_files(cls, bucket_name: Optional[str], storage_keys: List[str]) -> None:
        """Best-effort purge of Supabase Storage objects (used during account deletion)."""
        clean_keys = [k for k in storage_keys if k]
        if not clean_keys:
            return
        bucket = bucket_name or cls.BUCKET_NAME
        try:
            supabase_admin.storage.from_(bucket).remove(clean_keys)
        except Exception as exc:
            logger.warning(f"Best-effort storage cleanup failed on bucket '{bucket}': {exc}")


storage_service = StorageService()
