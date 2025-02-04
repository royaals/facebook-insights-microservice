from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from app.services.gridfs_service import GridFSService
from app.services.image_service import download_image
import os
import time

class FacebookScraper:
    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.gridfs_service = GridFSService()

    async def scrape_page(self, username):
        try:
            
            self.driver.get(f"https://www.facebook.com/{username}")
            time.sleep(5)  

            
            data = await self._scrape_basic_data()
            
            
            if data['profile_pic_url']:
                image_path = os.path.join('temp', 'profile_pic.jpg')
                os.makedirs('temp', exist_ok=True)
                
                
                await download_image(data['profile_pic_url'], image_path)
                uploaded_file = await self.gridfs_service.upload_file(image_path)
                data['profile_pic_url'] = uploaded_file.filename

            
            posts_data = await self._scrape_posts()
            data['posts'] = posts_data

            return data

        except Exception as e:
            print(f"Error scraping page {username}: {str(e)}")
            return None
        finally:
            self.driver.quit()

def _parse_number(self, text):
    try:
        
        text = text.strip().lower()
        
        
        if 'm' in text:
            number = float(text.replace('m', '').replace(',', '').strip())
            return int(number * 1000000)
        
        
        if 'k' in text:
            number = float(text.replace('k', '').replace(',', '').strip())
            return int(number * 1000)
        
        
        if 'b' in text:
            number = float(text.replace('b', '').replace(',', '').strip())
            return int(number * 1000000000)
        
        
        return int(float(text.replace(',', '').strip()))
    except:
        return 0

async def _scrape_basic_data(self):
    return self.driver.execute_script("""
        function parseCount(text) {
            if (!text) return 0;
            text = text.toLowerCase().trim();
            if (text.includes('m')) {
                return parseFloat(text.replace('m', '')) * 1000000;
            } else if (text.includes('k')) {
                return parseFloat(text.replace('k', '')) * 1000;
            } else if (text.includes('b')) {
                return parseFloat(text.replace('b', '')) * 1000000000;
            }
            return parseInt(text.replace(/[^0-9]/g, ''));
        }

        // Get followers count
        const followersText = document.querySelector('a[href*="followers/"]')?.innerText || 
                            document.querySelector('div[data-testid="page_followers"]')?.innerText || '0';
        const followers = parseCount(followersText);

        // Get likes count
        const likesText = document.querySelector('a[href*="friends_likes/"]')?.innerText || 
                         document.querySelector('div[data-testid="page_likes"]')?.innerText || '0';
        const likes = parseCount(likesText);

        return {
            page_name: document.title.split(" |")[0] || 'Unknown Page',
            profile_pic_url: document.querySelector('image[preserveAspectRatio="xMidYMid slice"]')?.getAttribute('xlink:href') || 
                           document.querySelector('img[data-imgperflogname="profileCoverPhoto"]')?.src || null,
            followers: followers,
            likes: likes,
            category: document.querySelector('div[data-testid="category"]')?.innerText || 'Unknown Category',
            email: document.querySelector('a[href^="mailto:"]')?.href.replace('mailto:', '') || null,
            website: document.querySelector('a[href^="http"]:not([href*="facebook.com"])')?.href || null,
            followers_type: 'Active',
            posts: []
        };
    """)

    async def _scrape_posts(self):
        return self.driver.execute_script("""
            const posts = [];
            const postElements = document.querySelectorAll('div[data-testid="post_message"]');

            postElements.forEach((postElement, index) => {
                if (index >= 25) return;  // Limit to 25 posts

                const postId = postElement.getAttribute('id') || `post_${index}`;
                const postContent = postElement.innerText || 'No Content';
                const comments = [];

                const commentElements = postElement.querySelectorAll('div[data-testid="comment"]');
                commentElements.forEach(commentElement => {
                    comments.push(commentElement.innerText || 'No Comment Text');
                });

                posts.push({
                    post_id: postId,
                    post_content: postContent,
                    comments: comments
                });
            });

            return posts;
        """)