from datetime import datetime
from bson import ObjectId

class SocialMediaUser:
    def __init__(self, fb_id, name, profile_pic=None, _id=None):
        self._id = _id or ObjectId()
        self.fb_id = fb_id
        self.name = name
        self.profile_pic = profile_pic
        self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            "_id": str(self._id),
            "fb_id": self.fb_id,
            "name": self.name,
            "profile_pic": self.profile_pic,
            "created_at": self.created_at
        }