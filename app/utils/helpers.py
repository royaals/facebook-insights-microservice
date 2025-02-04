from bson import ObjectId
import json
from datetime import datetime

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)

def format_number(num):
    """Convert numbers to K, M, B format"""
    if num >= 1000000000:
        return f"{num/1000000000:.1f}B"
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    if num >= 1000:
        return f"{num/1000:.1f}K"
    return str(num)

def format_page_response(page_data):
    """Format page data into desired response structure"""
    return {
        "page_id": str(page_data.get('_id')),
        "name": page_data.get('name'),
        "username": page_data.get('username'),
        "fb_id": page_data.get('fb_id'),
        "profile_pic": page_data.get('profile_pic'),
        "email": page_data.get('email'),
        "website": page_data.get('website'),
        "category": page_data.get('category'),
        "stats": {
            "followers_count": page_data.get('followers_count'),
            "likes_count": page_data.get('likes_count')
        },
        "creation_date": page_data.get('creation_date'),
        "ai_summary": page_data.get('ai_summary', {
            "page_type": "Business Page",
            "engagement_level": "Medium",
            "audience_demographics": "General audience",
            "content_strategy": "Regular updates"
        })
    }

def get_s3_url(bucket, key):
    """Generate S3 URL from bucket and key"""
    return f"https://{bucket}.s3.amazonaws.com/{key}"

def is_s3_url(url):
    """Check if URL is an S3 URL"""
    return 's3.amazonaws.com' in url

def extract_s3_key(url):
    """Extract S3 key from URL"""
    return url.split('.s3.amazonaws.com/')[-1]