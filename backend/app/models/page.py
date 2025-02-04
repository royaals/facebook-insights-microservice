from datetime import datetime
from bson import ObjectId

class Page:
    def __init__(self, name, username, fb_id, profile_pic=None, email=None, 
                 website=None, category=None, followers_count=0, likes_count=0, 
                 creation_date=None, _id=None):
        self._id = _id or ObjectId()
        self.name = name
        self.username = username
        self.fb_id = fb_id
        self.profile_pic = profile_pic
        self.email = email
        self.website = website
        self.category = category
        self.followers_count = followers_count
        self.likes_count = likes_count
        self.creation_date = creation_date
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def to_dict(self):
        return {
            "_id": str(self._id),
            "name": self.name,
            "username": self.username,
            "fb_id": self.fb_id,
            "profile_pic": self.profile_pic,
            "email": self.email,
            "website": self.website,
            "category": self.category,
            "followers_count": self.followers_count,
            "likes_count": self.likes_count,
            "creation_date": self.creation_date,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @staticmethod
    def from_dict(data):
        return Page(**data)