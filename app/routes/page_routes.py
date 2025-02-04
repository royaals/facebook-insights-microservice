from flask import Blueprint, jsonify, request
from app import mongo
from app.services.scraper import FacebookScraper
from app.services.ai_summary import AISummaryService
from app.models.page import Page

pages_bp = Blueprint('pages', __name__, url_prefix='/api')

@pages_bp.route('/', methods=['GET'])
def welcome():
    """Welcome endpoint with API information"""
    return jsonify({
        "success": True,
        "data": {
            "name": "Facebook Insights Microservice API",
            "version": "1.0.0",
            "description": "A service to analyze Facebook pages and provide insights",
            "endpoints": {
                "get_page": {
                    "method": "GET",
                    "url": "/api/pages/<username>",
                    "description": "Get Facebook page details and analytics",
                    "example": "/api/pages/nike"
                },
                "generate_summary": {
                    "method": "POST",
                    "url": "/api/pages/<username>/summary",
                    "description": "Generate AI-powered page analysis",
                    "example": "/api/pages/nike/summary"
                }
            },
            "status": {
                "service": "active",
                "database": "connected",
                "last_updated": datetime.utcnow().isoformat(),
                "timezone": "UTC"
            },
            "documentation": {
                "github": "https://github.com/yourusername/facebook-insights-api",
                "postman": "Link to Postman collection"
            },
            "contact": {
                "developer": "Your Name",
                "email": "your.email@example.com",
                "github": "https://github.com/yourusername"
            }
        },
        "meta": {
            "timestamp": datetime.utcnow().isoformat(),
            "server_time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        }
    })

@pages_bp.route('/pages/<username>', methods=['GET'])
async def get_page(username):
    try:
        
        existing_page = mongo.db.pages.find_one({'username': username.lower()})
        
        if not existing_page:
            
            scraper = FacebookScraper()
            scraped_data = await scraper.scrape_page(username)
            
            if scraped_data:
                
                page_data = {
                    'page_name': scraped_data.get('page_name'),
                    'username': username,
                    'page_url': f"https://facebook.com/{username}",
                    'profile_pic_url': scraped_data.get('profile_pic_url'),
                    'email': scraped_data.get('email'),
                    'website': scraped_data.get('website'),
                    'category': scraped_data.get('category'),
                    'followers': int(scraped_data.get('followers', 0)),
                    'likes': int(scraped_data.get('likes', 0)),
                    'posts': scraped_data.get('posts', []),
                    'followers_type': scraped_data.get('followers_type', 'Active')
                }

                # Create and save page
                page = Page(**page_data)
                page_dict = page.to_dict()
                mongo.db.pages.insert_one(page_dict)
                
                return jsonify({
                    "success": True,
                    "data": page_dict
                })
            
            return jsonify({
                "success": False,
                "error": "Page not found"
            }), 404
        
        return jsonify({
            "success": True,
            "data": existing_page
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@pages_bp.route('/pages/<username>/summary', methods=['GET', 'POST'])
async def generate_page_summary(username):
    try:
        
        page = mongo.db.pages.find_one({'username': username.lower()})
        if not page:
            return jsonify({
                "success": False,
                "error": "Page not found"
            }), 404

        
        followers = page.get('followers', 0)
        likes = page.get('likes', 0)

        
        ai_service = AISummaryService()
        summary = await ai_service.generate_summary(page)
        
        if not summary:
            return jsonify({
                "success": False,
                "error": "Failed to generate summary"
            }), 500

        
        mongo.db.pages.update_one(
            {'username': username.lower()},
            {'$set': {'ai_summary': summary}}
        )

        return jsonify({
            "success": True,
            "data": {
                "page_name": page.get('page_name'),
                "category": page.get('category'),
                "stats": {
                    "followers": followers,
                    "likes": likes,
                    "followers_formatted": f"{followers:,}",
                    "likes_formatted": f"{likes:,}"
                },
                "ai_summary": summary
            }
        })

    except Exception as e:
        print(f"Error in generate_page_summary: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500