import boto3
from botocore.exceptions import ClientError
from app.core.config import settings
from typing import BinaryIO
import uuid
import os
from pathlib import Path


class StorageService:
    def __init__(self):
        # Only initialize S3 client if credentials are provided
        self.has_s3_config = bool(settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY and settings.S3_BUCKET_NAME)
        if self.has_s3_config:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
            self.bucket_name = settings.S3_BUCKET_NAME
        else:
            # Use local storage as fallback
            self.local_storage_dir = os.path.join(os.getcwd(), 'local_storage', 'uploads')
            os.makedirs(self.local_storage_dir, exist_ok=True)
    
    async def upload_file(self, file_obj: BinaryIO, key: str) -> str:
        """Upload file to S3 or local storage and return URL"""
        try:
            # Generate unique key if needed
            if not key:
                key = f"uploads/{uuid.uuid4()}"
            
            if self.has_s3_config:
                # Upload to S3
                self.s3_client.upload_fileobj(
                    file_obj,
                    self.bucket_name,
                    key,
                    ExtraArgs={'ACL': 'public-read'}
                )
                # Return public URL
                url = f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{key}"
                return url
            else:
                # Fallback to local storage for development
                # Use unique filename to avoid conflicts
                import uuid
                original_file_name = os.path.basename(key) if '/' in key else key
                file_ext = os.path.splitext(original_file_name)[1] or '.jpg'
                unique_file_name = f"{uuid.uuid4()}{file_ext}"
                file_path = os.path.join(self.local_storage_dir, unique_file_name)
                
                # Read file content and write to local storage
                file_obj.seek(0)
                content = file_obj.read()
                with open(file_path, 'wb') as f:
                    f.write(content)
                
                # Return local file path (served by the backend)
                return f"{settings.API_BASE_URL}/local_storage/uploads/{unique_file_name}"
        except ClientError as e:
            raise Exception(f"Failed to upload file to S3: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to upload file: {str(e)}")
    
    async def delete_file(self, url: str):
        """Delete file from S3"""
        try:
            # Extract key from URL
            key = url.split(f"{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/")[-1]
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
        except ClientError as e:
            print(f"Failed to delete file: {str(e)}")
    
    async def download_file(self, key: str) -> bytes:
        """Download file from S3"""
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            return response['Body'].read()
        except ClientError as e:
            raise Exception(f"Failed to download file: {str(e)}")






