import logging

import boto3
from botocore.client import Config
from core.config import settings

logger = logging.getLogger(__name__)


class S3Client:
    def __init__(self):
        self.internal_endpoint = settings.S3_INTERNAL_ENDPOINT
        self.public_endpoint = settings.S3_PUBLIC_ENDPOINT
        self.access_key = settings.S3_ACCESS_KEY
        self.secret_key = settings.S3_SECRET_KEY
        self.bucket_name = settings.S3_BUCKET

        self.client = boto3.client(
            "s3",
            endpoint_url=self.internal_endpoint,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            config=Config(signature_version="s3v4"),
            region_name="us-east-1",
        )
        self._ensure_bucket()

    def _ensure_bucket(self):
        try:
            self.client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"Bucket {self.bucket_name} exists")
        except Exception:
            logger.info(f"Creating bucket {self.bucket_name}")
            self.client.create_bucket(Bucket=self.bucket_name)

    def upload_file(self, local_path: str, s3_key: str) -> str:
        """Загружает файл и возвращает ПУБЛИЧНЫЙ URL"""
        self.client.upload_file(local_path, self.bucket_name, s3_key)
        public_url = f"{self.public_endpoint}/{self.bucket_name}/{s3_key}"
        logger.info(f"Uploaded {s3_key}, public URL: {public_url}")
        return public_url

    def delete_file(self, s3_key: str) -> bool:
        """Удаляет файл из S3"""
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            logger.info(f"Deleted {s3_key}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete {s3_key}: {e}")
            return False


s3_client = S3Client()
