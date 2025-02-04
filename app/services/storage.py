import boto3
import requests
from botocore.exceptions import ClientError
from app.config import Config
import hashlib
from datetime import datetime

class StorageService:
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=Config.AWS_ACCESS_KEY,
            aws_secret_access_key=Config.AWS_SECRET_KEY,
            region_name=Config.AWS_REGION
        )
        self.bucket = Config.S3_BUCKET

    async def store_image(self, image_url, folder='profiles'):
        try:
            if not image_url:
                return None

            
            file_extension = self._get_file_extension(image_url)
            filename = self._generate_unique_filename(image_url, file_extension)
            key = f"{folder}/{filename}"

            
            response = requests.get(image_url)
            if response.status_code != 200:
                return image_url

            
            self.s3.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=response.content,
                ContentType=f'image/{file_extension}',
                ACL='public-read'
            )

            return f"https://{self.bucket}.s3.amazonaws.com/{key}"

        except Exception as e:
            print(f"Error storing image: {str(e)}")
            return image_url

    def _get_file_extension(self, url):
        extension = url.split('.')[-1].lower()
        if extension in ['jpg', 'jpeg', 'png', 'gif']:
            return extension
        return 'jpg'

    def _generate_unique_filename(self, url, extension):
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        url_hash = hashlib.md5(url.encode()).hexdigest()[:10]
        return f"{timestamp}_{url_hash}.{extension}"