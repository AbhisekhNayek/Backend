import boto3
import uuid
import logging
from app.config import settings

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self):
        self.s3_client = boto3.client(
            "s3",
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key
        )
        self.bucket_name = settings.aws_s3_bucket

    def upload_file(self, file_content: bytes, original_filename: str, mimetype: str, folder: str = "others") -> str:
        try:
            file_extension = original_filename.split(".")[-1] if "." in original_filename else "bin"
            file_name = f"{folder}/{uuid.uuid4()}.{file_extension}"

            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_name,
                Body=file_content,
                ContentType=mimetype
            )

            # Return the public URL matching standard S3 formats
            return f"https://{self.bucket_name}.s3.{settings.aws_region}.amazonaws.com/{file_name}"
        except Exception as e:
            logger.error(f"[STORAGE] Upload error: {str(e)}")
            raise Exception("Failed to upload file to storage")

storage_service = StorageService()
