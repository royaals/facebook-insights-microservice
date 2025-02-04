from bson import ObjectId
import json

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if hasattr(o, 'isoformat'):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)

def format_number(num):
    """Convert numbers to K, M, B format"""
    if num >= 1000000000:
        return f"{num/1000000000:.1f}B"
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    if num >= 1000:
        return f"{num/1000:.1f}K"
    return str(num)