from datetime import datetime
from bson import ObjectId

class Comment:
    def __init__(self, post_id, user_id, content, likes_count=0, _id=None):
        self._id = _id or ObjectId()
        self.post_id = post_id
        self.user_id = user_id
        self.content = content
        self.likes_count = likes_count
        self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            "_id": str(self._id),
            "post_id": str(self.post_id),
            "user_id": str(self.user_id),
            "content": self.content,
            "likes_count": self.likes_count,
            "created_at": self.created_at
        }