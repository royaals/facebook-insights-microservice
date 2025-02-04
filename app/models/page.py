from datetime import datetime
from bson import ObjectId

class Page:
    def __init__(self, page_name, username=None, page_url=None, profile_pic_url=None, 
                 email=None, website=None, category=None, followers=0, likes=0, 
                 posts=None, followers_type=None, _id=None):
        self._id = _id or ObjectId()
        self.page_name = page_name
        self.username = username
        self.page_url = page_url
        self.profile_pic = profile_pic_url  
        self.email = email
        self.website = website
        self.category = category
        self.followers = followers
        self.likes = likes
        self.posts = posts or []
        self.followers_type = followers_type
        self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            "_id": str(self._id),
            "page_name": self.page_name,
            "username": self.username,
            "page_url": self.page_url,
            "profile_pic": self.profile_pic,
            "email": self.email,
            "website": self.website,
            "category": self.category,
            "followers": self.followers,
            "likes": self.likes,
            "posts": self.posts,
            "followers_type": self.followers_type,
            "created_at": self.created_at
        }

    @staticmethod
    def from_dict(data):
        return Page(**data)