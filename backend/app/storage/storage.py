import os
import aioboto3
from contextlib import asynccontextmanager

class StorageClient:
    def __init__(self):
        self.bucket = os.getenv("S3_BUCKET", "uploads")
        self.endpoint = os.getenv("S3_ENDPOINT")
        self.key = os.getenv("S3_KEY_ID")
        self.secret = os.getenv("S3_SECRET_ACCESS_KEY")
        self.region = os.getenv("S3_REGION", "us-east-1")
        self.use_ssl = os.getenv("S3_USE_SSL", "false").lower() == "true"

    @asynccontextmanager
    async def get_s3(self):
        session = aioboto3.Session()
        async with session.resource(
            "s3",
            endpoint_url=self.endpoint,
            aws_access_key_id=self.key,
            aws_secret_access_key=self.secret,
            region_name=self.region,
            use_ssl=self.use_ssl
        ) as s3:
            bucket = await s3.Bucket(self.bucket)
            if not await bucket.creation_date:
                await s3.create_bucket(Bucket=self.bucket)
            yield s3

    async def upload_file(self, key: str, data: bytes) -> str:
        async with self.get_s3() as s3:
            bucket = await s3.Bucket(self.bucket)
            await bucket.put_object(Key=key, Body=data)
            return key

    async def download_file(self, key: str) -> bytes:
        async with self.get_s3() as s3:
            bucket = await s3.Bucket(self.bucket)
            obj = await bucket.Object(key)
            resp = await obj.get()
            return await resp["Body"].read()

    async def delete_file(self, key: str):
        async with self.get_s3() as s3:
            bucket = await s3.Bucket(self.bucket)
            obj = await bucket.Object(key)
            await obj.delete()
