import openai
from app.config import Config

class AISummaryService:
    def __init__(self):
        self.api_key = Config.OPENAI_API_KEY
        openai.api_key = self.api_key
    def _format_number(self, num):
        if num >= 1000000:
         return f"{num/1000000:.1f}M"
        elif num >= 1000:
         return f"{num/1000:.1f}K"
        return str(num)
    async def generate_summary(self, page_data):
        try:
            if not self.api_key:
                raise ValueError("OpenAI API key not configured")

            # Prepare the analysis data
            followers = page_data.get('followers', 0)
            likes = page_data.get('likes', 0)
            category = page_data.get('category', 'Unknown')
            name = page_data.get('page_name', 'Unknown')

            formatted_followers = self._format_number(followers)
            formatted_likes = self._format_number(likes)

            prompt = f"""
            Analyze this Facebook page:
            Name: {name}
            Category: {category}
            Followers: {formatted_followers}
            Likes: {formatted_likes}

            Provide a brief analysis covering:
            1. Brand positioning and market presence
            2. Audience engagement and reach
            3. Content effectiveness
            4. Growth potential and recommendations
            """

            try:
                completion = await openai.ChatCompletion.acreate(
                    model="deepseek/deepseek-r1:free",
                    messages=[
                        {"role": "system", "content": "You are an expert social media analyst."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=300,
                    temperature=0.7
                )
                main_summary = completion.choices[0].message.content
            except Exception as e:
                print(f"OpenAI API error: {str(e)}")
                main_summary = self._generate_fallback_summary(page_data)

            # Determine engagement metrics
            engagement_level = self._calculate_engagement_level(followers)
            page_type = self._determine_page_type(category)
            content_strategy = self._suggest_content_strategy(category)
            engagement_rate = round((likes / followers * 100 if followers > 0 else 0), 2)

            return {
                "summary": main_summary,
                "page_type": page_type,
                "engagement_level": engagement_level,
                "content_strategy": content_strategy,
                "metrics": {
                    "followers": followers,
                    "likes": likes,
                    "engagement_rate": engagement_rate
                },
                "recommendations": self._generate_recommendations(category, engagement_level)
            }

        except Exception as e:
            print(f"Error in generate_summary: {str(e)}")
            return self._generate_fallback_summary(page_data)

    def _calculate_engagement_level(self, followers):
        if followers >= 1000000:
            return "Very High"
        elif followers >= 100000:
            return "High"
        elif followers >= 10000:
            return "Medium"
        return "Low"

    def _determine_page_type(self, category):
        category_lower = category.lower()
        if 'tech' in category_lower or 'electronics' in category_lower:
            return "Technology Brand"
        elif 'sport' in category_lower or 'athlet' in category_lower:
            return "Sports Brand"
        elif 'food' in category_lower or 'restaurant' in category_lower:
            return "Food & Beverage"
        elif 'retail' in category_lower or 'shop' in category_lower:
            return "Retail Business"
        return "Business Page"

    def _suggest_content_strategy(self, category):
        category_lower = category.lower()
        if 'tech' in category_lower:
            return "Product launches, innovation stories, tech updates"
        elif 'sport' in category_lower:
            return "Product launches, athlete stories, fitness motivation"
        elif 'food' in category_lower:
            return "Food photography, recipes, special offers"
        return "Regular updates, customer engagement, industry news"

    def _generate_recommendations(self, category, engagement_level):
        base_recommendations = [
            "Maintain consistent posting schedule",
            "Engage with follower comments regularly",
            "Use high-quality visuals"
        ]

        category_lower = category.lower()
        if 'tech' in category_lower:
            base_recommendations.extend([
                "Share product tutorials and tips",
                "Highlight innovation stories",
                "Feature customer success stories"
            ])
        elif 'sport' in category_lower:
            base_recommendations.extend([
                "Share workout tips and routines",
                "Feature athlete testimonials",
                "Post motivational content"
            ])

        return base_recommendations

    def _generate_fallback_summary(self, page_data):
        """Generate a basic summary when OpenAI API fails"""
        followers = page_data.get('followers', 0)
        category = page_data.get('category', 'Unknown')
        name = page_data.get('page_name', 'Unknown')

        engagement_level = self._calculate_engagement_level(followers)
        page_type = self._determine_page_type(category)
        content_strategy = self._suggest_content_strategy(category)

        return {
            "summary": f"{name} is a {page_type} with {followers:,} followers. " +
                      f"The page shows {engagement_level.lower()} engagement levels.",
            "page_type": page_type,
            "engagement_level": engagement_level,
            "content_strategy": content_strategy,
            "metrics": {
                "followers": followers,
                "likes": page_data.get('likes', 0),
                "engagement_rate": round((page_data.get('likes', 0) / followers * 100 if followers > 0 else 0), 2)
            },
            "recommendations": self._generate_recommendations(category, engagement_level)
        }