from datetime import datetime
from bson import ObjectId

class Page:
    def __init__(self, page_name, page_url=None, profile_pic=None, email=None, 
                 website=None, category=None, followers=0, likes=0, posts=None, 
                 followers_data=None, _id=None):
        self._id = _id or ObjectId()
        self.page_name = page_name
        self.page_url = page_url
        self.profile_pic = profile_pic
        self.email = email
        self.website = website
        self.category = category
        self.followers = followers
        self.likes = likes
        self.created_at = datetime.utcnow()
        self.posts = posts or []
        self.followers_data = followers_data or []

    def to_dict(self):
        return {
            "_id": str(self._id),
            "page_name": self.page_name,
            "page_url": self.page_url,
            "profile_pic": self.profile_pic,
            "email": self.email,
            "website": self.website,
            "category": self.category,
            "followers": self.followers,
            "likes": self.likes,
            "created_at": self.created_at,
            "posts": self.posts,
            "followers_data": self.followers_data
        }

    @staticmethod
    def from_dict(data):
        return Page(**data)