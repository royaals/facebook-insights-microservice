from datetime import datetime
from bson import ObjectId

class Post:
    def __init__(self, page_id, content, post_url, likes_count=0, 
                 comments_count=0, shares_count=0, _id=None):
        self._id = _id or ObjectId()
        self.page_id = page_id
        self.content = content
        self.post_url = post_url
        self.likes_count = likes_count
        self.comments_count = comments_count
        self.shares_count = shares_count
        self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            "_id": str(self._id),
            "page_id": str(self.page_id),
            "content": self.content,
            "post_url": self.post_url,
            "likes_count": self.likes_count,
            "comments_count": self.comments_count,
            "shares_count": self.shares_count,
            "created_at": self.created_at
        }