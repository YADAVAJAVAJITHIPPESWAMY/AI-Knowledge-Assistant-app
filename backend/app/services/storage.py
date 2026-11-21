"""
Storage Service
Supports MinIO (S3-compatible) and local filesystem fallback.
Provides secure upload, download, SHA-256 checksum calculation, and deletion.
"""
import os
import hashlib
from typing import Optional, Tuple
from app.core.config import settings

# Try importing MinIO client
try:
    from minio import Minio
    from minio.error import S3Error
    HAS_MINIO = True
except ImportError:
    HAS_MINIO = False
    Minio = None
    S3Error = Exception


class StorageService:
    def __init__(self):
        self.use_s3 = False
        self.client = None
        self.bucket = settings.S3_BUCKET_NAME
        self.local_dir = settings.LOCAL_STORAGE_DIR

        # Ensure local storage directory exists
        os.makedirs(self.local_dir, exist_ok=True)

        if HAS_MINIO and settings.S3_ENDPOINT:
            try:
                # Remove http:// or https:// from endpoint for minio client if needed
                endpoint = settings.S3_ENDPOINT.replace("http://", "").replace("https://", "")
                self.client = Minio(
                    endpoint=endpoint,
                    access_key=settings.S3_ACCESS_KEY,
                    secret_key=settings.S3_SECRET_KEY,
                    secure=settings.S3_USE_SSL,
                )
                # Attempt to ensure bucket exists
                if not self.client.bucket_exists(self.bucket):
                    self.client.make_bucket(self.bucket)
                self.use_s3 = True
            except Exception:
                # Fallback to local storage if MinIO is unreachable
                self.use_s3 = False

    @staticmethod
    def compute_checksum(data: bytes) -> str:
        """Computes SHA-256 checksum of raw file bytes."""
        return hashlib.sha256(data).hexdigest()

    def save_file(self, file_bytes: bytes, user_id: str, filename: str) -> Tuple[str, str]:
        """
        Saves a user file in object storage or local disk.
        Returns: (storage_path, checksum)
        """
        checksum = self.compute_checksum(file_bytes)
        safe_filename = "".join(c for c in filename if c.isalnum() or c in (".", "-", "_"))
        storage_key = f"users/{user_id}/{checksum[:12]}_{safe_filename}"

        if self.use_s3 and self.client:
            try:
                import io
                self.client.put_object(
                    bucket_name=self.bucket,
                    object_name=storage_key,
                    data=io.BytesIO(file_bytes),
                    length=len(file_bytes),
                )
                return storage_key, checksum
            except Exception:
                pass  # Fall back to local file system

        # Local filesystem fallback
        local_user_dir = os.path.join(self.local_dir, "users", str(user_id))
        os.makedirs(local_user_dir, exist_ok=True)
        local_file_path = os.path.join(local_user_dir, f"{checksum[:12]}_{safe_filename}")
        with open(local_file_path, "wb") as f:
            f.write(file_bytes)

        return local_file_path, checksum

    def get_file(self, storage_path: str) -> Optional[bytes]:
        """Retrieves raw file bytes from storage."""
        if self.use_s3 and self.client and not os.path.isabs(storage_path):
            try:
                response = self.client.get_object(self.bucket, storage_path)
                data = response.read()
                response.close()
                response.release_conn()
                return data
            except Exception:
                pass

        # Check local path
        if os.path.exists(storage_path):
            with open(storage_path, "rb") as f:
                return f.read()
        return None

    def delete_file(self, storage_path: str) -> bool:
        """Deletes file from storage."""
        if self.use_s3 and self.client and not os.path.isabs(storage_path):
            try:
                self.client.remove_object(self.bucket, storage_path)
                return True
            except Exception:
                pass

        if os.path.exists(storage_path):
            try:
                os.remove(storage_path)
                return True
            except Exception:
                return False
        return True


storage_service = StorageService()
