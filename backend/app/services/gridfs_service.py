from app import mongo
import gridfs
import os

class GridFSService:
    def __init__(self):
        self.fs = gridfs.GridFS(mongo.db)

    async def upload_file(self, file_path):
        try:
            filename = os.path.basename(file_path)
            
            with open(file_path, 'rb') as f:
                file_id = self.fs.put(
                    f.read(),
                    filename=filename,
                    content_type='image/jpeg'
                )
            
            # Clean up the temporary file
            os.remove(file_path)
            
            return self.fs.get(file_id)
        except Exception as e:
            print(f"Error uploading to GridFS: {str(e)}")
            return None

    def get_file(self, filename):
        try:
            return self.fs.find_one({"filename": filename})
        except Exception as e:
            print(f"Error retrieving from GridFS: {str(e)}")
            return None