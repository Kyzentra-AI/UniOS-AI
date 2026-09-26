from app.core.supabase import supabase_admin
import uuid

class StorageService:
    BUCKET_NAME = "syllabi"
    
    @classmethod
    def upload_file(cls, file_bytes: bytes, file_name: str, content_type: str = "application/pdf") -> str:
        file_ext = file_name.split('.')[-1] if '.' in file_name else 'pdf'
        unique_name = f"{uuid.uuid4()}.{file_ext}"
        storage_key = f"uploads/{unique_name}"
        
        # Uploading to Supabase Storage
        # If the bucket doesn't exist, this will throw an error, 
        # so ensure bucket is created in Supabase.
        supabase_admin.storage.from_(cls.BUCKET_NAME).upload(
            path=storage_key,
            file=file_bytes,
            file_options={"content-type": content_type}
        )
        return storage_key

storage_service = StorageService()
