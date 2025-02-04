import aiohttp
import aiofiles
import os

async def download_image(url: str, file_path: str) -> bool:
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    async with aiofiles.open(file_path, mode='wb') as f:
                        await f.write(await response.read())
                    return True
                return False
    except Exception as e:
        print(f"Error downloading image: {str(e)}")
        return False