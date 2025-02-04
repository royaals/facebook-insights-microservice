import openai
from app.config import Config

class AISummary:
    def __init__(self):
        openai.api_key = Config.OPENAI_API_KEY

    def generate_page_summary(self, page_data):
        try:
            prompt = self._create_prompt(page_data)
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a social media analyst."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            return {
                "page_type": self._determine_page_type(page_data),
                "engagement_level": self._calculate_engagement_level(page_data),
                "audience_demographics": response.choices[0].message.content,
                "content_strategy": self._suggest_content_strategy(page_data)
            }
        except Exception as e:
            print(f"Error generating AI summary: {str(e)}")
            return None

    def _create_prompt(self, page_data):
        return f"""
        Analyze this Facebook page:
        Name: {page_data.get('name')}
        Category: {page_data.get('category')}
        Followers: {page_data.get('followers_count')}
        Likes: {page_data.get('likes_count')}
        
        Please provide a brief analysis of the target audience demographics.
        """

    def _determine_page_type(self, page_data):
        category = page_data.get('category', '').lower()
        if 'tech' in category:
            return "Technology Brand"
        elif 'sport' in category:
            return "Sports Brand"
        elif 'food' in category:
            return "Food & Beverage"
        return "Business Page"

    def _calculate_engagement_level(self, page_data):
        followers = page_data.get('followers_count', 0)
        if followers > 1000000:
            return "Very High"
        elif followers > 100000:
            return "High"
        elif followers > 10000:
            return "Medium"
        return "Low"

    def _suggest_content_strategy(self, page_data):
        category = page_data.get('category', '').lower()
        if 'tech' in category:
            return "Product launches, innovation stories, tech tips"
        elif 'sport' in category:
            return "Product launches, athlete stories, fitness tips"
        elif 'food' in category:
            return "Recipe sharing, food photography, cooking tips"
        return "Regular updates, customer engagement, industry news"