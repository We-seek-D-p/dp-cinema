import boto3
from botocore.client import Config
from core.config import settings


class S3Client:
    def __init__(self):
        self.endpoint = settings.S3_ENDPOINT
        self.access_key = settings.S3_ACCESS_KEY
        self.secret_key = settings.S3_SECRET_KEY
        self.bucket_name = settings.S3_BUCKET

        self.client = boto3.client(
            's3',
            endpoint_url=self.endpoint,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            config=Config(signature_version='s3v4'),
            region_name='us-east-1'
        )
        self._ensure_bucket()

    def _ensure_bucket(self):
        try:
            self.client.head_bucket(Bucket=self.bucket_name)
        except Exception:
            self.client.create_bucket(Bucket=self.bucket_name)

    def upload_file(self, local_path: str, s3_key: str):
        self.client.upload_file(local_path, self.bucket_name, s3_key)
        return f"{self.endpoint}/{self.bucket_name}/{s3_key}"


s3_client = S3Client()
