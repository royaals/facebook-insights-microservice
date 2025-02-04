import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from app.models.page import Page
from app.services.storage import StorageService
import time
import re
from app.config import Config

class FacebookScraper:
    def __init__(self):
        # Setup Selenium with authentication
        self.chrome_options = Options()
        # self.chrome_options.add_argument('--headless')  # Comment this for debugging
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--disable-notifications')
        self.chrome_options.add_argument('--start-maximized')
        
        # Setup ChromeDriver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=self.chrome_options)
        
        # Initialize storage service
        self.storage = StorageService()
        
        # Facebook credentials from config
        self.fb_email = Config.FACEBOOK_EMAIL
        self.fb_password = Config.FACEBOOK_PASSWORD
        
        # Login to Facebook
        self._facebook_login()

    def _facebook_login(self):
        try:
            self.driver.get('https://www.facebook.com')
            time.sleep(3)  # Wait for page to load

            # Find and fill email
            email_field = self.driver.find_element(By.ID, 'email')
            email_field.send_keys(self.fb_email)

            # Find and fill password
            password_field = self.driver.find_element(By.ID, 'pass')
            password_field.send_keys(self.fb_password)

            # Click login button
            login_button = self.driver.find_element(By.NAME, 'login')
            login_button.click()

            time.sleep(5)  # Wait for login to complete
            
        except Exception as e:
            print(f"Login error: {str(e)}")

    async def scrape_page(self, username):
        try:
            url = f"https://www.facebook.com/{username}"
            self.driver.get(url)
            time.sleep(5)  # Wait for page to load

            # Scroll to load more content
            self._scroll_page()

            # Get page source after JavaScript execution
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')

            # Extract all page data
            page_data = await self._extract_page_data(soup, username)
            
            if page_data:
                return Page(**page_data)
            return None

        except Exception as e:
            print(f"Error scraping page {username}: {str(e)}")
            return None

    def _scroll_page(self):
        for _ in range(3):  # Scroll 3 times
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

    async def _extract_page_data(self, soup, username):
        try:
            # Extract name
            name = self._extract_name(soup)
            if not name:
                return None

            # Extract and store profile picture
            profile_pic = await self._extract_and_store_profile_pic(soup, username)

            # Extract page info
            about_data = self._extract_about_info(soup)
            stats_data = self._extract_stats(soup)

            page_data = {
                'name': name,
                'username': username,
                'fb_id': self._extract_fb_id(soup),
                'profile_pic': profile_pic,
                'email': about_data.get('email'),
                'website': about_data.get('website'),
                'category': about_data.get('category'),
                'followers_count': stats_data.get('followers_count', 0),
                'likes_count': stats_data.get('likes_count', 0),
                'creation_date': about_data.get('creation_date'),
            }

            # Generate AI summary based on extracted data
            page_data['ai_summary'] = self._generate_ai_summary(page_data)

            return page_data

        except Exception as e:
            print(f"Error extracting page data: {str(e)}")
            return None

    def _extract_name(self, soup):
        try:
            # Try different selectors for name
            name_element = soup.find('h1')
            if name_element:
                return name_element.text.strip()
            return None
        except Exception as e:
            print(f"Error extracting name: {str(e)}")
            return None

    async def _extract_and_store_profile_pic(self, soup, username):
        try:
            img_element = soup.find('image', {'class': 'silenthedger'}) or \
                         soup.find('img', {'class': 'profilephoto'})
            
            if img_element and img_element.get('xlink:href'):
                profile_pic_url = img_element['xlink:href']
                return await self.storage.store_image(profile_pic_url, f"profiles/{username}")
            return None
        except Exception as e:
            print(f"Error extracting profile picture: {str(e)}")
            return None

    def _extract_about_info(self, soup):
        about_data = {
            'email': None,
            'website': None,
            'category': None,
            'creation_date': None
        }

        try:
            # Click About tab if available
            about_link = self.driver.find_element(By.XPATH, "//div[contains(text(), 'About')]")
            about_link.click()
            time.sleep(3)

            # Get updated page source
            about_soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            # Extract category
            category_element = about_soup.find('div', text=re.compile(r'Category'))
            if category_element:
                about_data['category'] = category_element.find_next('span').text.strip()

            # Extract website
            website_element = about_soup.find('div', text=re.compile(r'Website'))
            if website_element:
                about_data['website'] = website_element.find_next('a')['href']

            # Extract email
            email_element = about_soup.find(text=re.compile(r'[\w\.-]+@[\w\.-]+\.\w+'))
            if email_element:
                about_data['email'] = email_element.strip()

            # Extract creation date
            date_element = about_soup.find('div', text=re.compile(r'Founded|Started|Created'))
            if date_element:
                date_text = date_element.find_next('span').text.strip()
                about_data['creation_date'] = self._parse_date(date_text)

        except Exception as e:
            print(f"Error extracting about info: {str(e)}")

        return about_data

    def _extract_stats(self, soup):
        stats = {
            'followers_count': 0,
            'likes_count': 0
        }

        try:
            # Extract followers count
            followers_element = soup.find(text=re.compile(r'[\d,.]+ (followers|people follow this)'))
            if followers_element:
                stats['followers_count'] = self._parse_count(followers_element)

            # Extract likes count
            likes_element = soup.find(text=re.compile(r'[\d,.]+ (likes|people like this)'))
            if likes_element:
                stats['likes_count'] = self._parse_count(likes_element)

        except Exception as e:
            print(f"Error extracting stats: {str(e)}")

        return stats

    def _parse_count(self, text):
        try:
            number = re.search(r'[\d,.]+', text).group(0)
            number = number.replace(',', '')
            
            if 'K' in text:
                return int(float(number) * 1000)
            elif 'M' in text:
                return int(float(number) * 1000000)
            elif 'B' in text:
                return int(float(number) * 1000000000)
            
            return int(float(number))
        except:
            return 0

    def _parse_date(self, date_text):
        try:
            # Add your date parsing logic here
            # Example: "Founded in 2009" -> "2009-01-01T00:00:00Z"
            year_match = re.search(r'\d{4}', date_text)
            if year_match:
                return f"{year_match.group(0)}-01-01T00:00:00Z"
            return None
        except:
            return None

    def _generate_ai_summary(self, page_data):
        category = page_data.get('category', '').lower()
        followers = page_data.get('followers_count', 0)

        # Determine page type
        if 'sport' in category or 'athletic' in category:
            page_type = "Global Sports Brand"
            audience = "Sports enthusiasts, athletes, fitness-focused consumers"
            content = "Product launches, athlete stories, motivational content"
        elif 'tech' in category:
            page_type = "Technology Brand"
            audience = "Tech enthusiasts, early adopters, professionals"
            content = "Product launches, innovation stories, tech updates"
        else:
            page_type = "Business Page"
            audience = "General audience"
            content = "Regular updates"

        # Determine engagement level
        if followers > 1000000:
            engagement = "Very High"
        elif followers > 100000:
            engagement = "High"
        elif followers > 10000:
            engagement = "Medium"
        else:
            engagement = "Low"

        return {
            "page_type": page_type,
            "engagement_level": engagement,
            "audience_demographics": audience,
            "content_strategy": content
        }

    def __del__(self):
        try:
            self.driver.quit()
        except:
            pass