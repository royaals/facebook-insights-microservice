from flask import Blueprint, jsonify, request
from datetime import datetime
from bson import ObjectId
from app import mongo
from app.services.scraper import FacebookScraper
from app.services.ai_summary import AISummaryService
from app.models.page import Page

pages_bp = Blueprint('pages', __name__, url_prefix='/api')

from flask import Blueprint, jsonify, request
from datetime import datetime
from bson import ObjectId
from app import mongo
from app.services.scraper import FacebookScraper
from app.services.ai_summary import AISummaryService
from app.models.page import Page

# Change the blueprint registration
pages_bp = Blueprint('pages', __name__)  # Remove url_prefix here

@pages_bp.route('/', methods=['GET'])
def welcome():
    """Welcome endpoint with API information"""
    try:
        # Check MongoDB connection
        db_status = "connected" if mongo.db.command('ping') else "disconnected"
    except Exception:
        db_status = "disconnected"

    return jsonify({
        "success": True,
        "data": {
            "service": {
                "name": "Facebook Insights Microservice API",
                "version": "1.0.0",
                "description": "Analyze Facebook pages and generate AI-powered insights",
                "status": "operational"
            },
            "endpoints": {
                "root": {
                    "method": "GET",
                    "url": "/",
                    "description": "Welcome page and API information"
                },
                "get_page": {
                    "method": "GET",
                    "url": "/pages/<username>",
                    "description": "Get Facebook page details and analytics",
                    "example": "/pages/nike"
                },
                "generate_summary": {
                    "method": "POST",
                    "url": "/pages/<username>/summary",
                    "description": "Generate AI-powered page analysis",
                    "example": "/pages/nike/summary"
                }
            },
            "status": {
                "service": "active",
                "database": db_status,
                "last_updated": datetime.utcnow().isoformat(),
                "timezone": "UTC"
            }
        },
        "meta": {
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": str(ObjectId())
        }
    })

@pages_bp.route('/pages/<username>', methods=['GET'])
async def get_page(username):
    try:
        # Check if page exists in DB
        existing_page = mongo.db.pages.find_one({'username': username.lower()})
        
        if not existing_page:
            # Scrape page if not in DB
            scraper = FacebookScraper()
            scraped_data = await scraper.scrape_page(username)
            
            if scraped_data:
                # Format page data
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
                    'followers_type': scraped_data.get('followers_type', 'Active'),
                    'created_at': datetime.utcnow(),
                    'updated_at': datetime.utcnow()
                }

                # Create and save page
                page = Page(**page_data)
                page_dict = page.to_dict()
                mongo.db.pages.insert_one(page_dict)
                
                return jsonify({
                    "success": True,
                    "data": page_dict,
                    "meta": {
                        "timestamp": datetime.utcnow().isoformat(),
                        "request_id": str(ObjectId())
                    }
                })
            
            return jsonify({
                "success": False,
                "error": {
                    "code": "PAGE_NOT_FOUND",
                    "message": "Page not found or could not be scraped"
                }
            }), 404
        
        return jsonify({
            "success": True,
            "data": existing_page,
            "meta": {
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": str(ObjectId())
            }
        })
    
    except Exception as e:
        print(f"Error in get_page: {str(e)}")
        return jsonify({
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": str(e)
            }
        }), 500

@pages_bp.route('/pages/<username>/summary', methods=['GET', 'POST'])
async def generate_page_summary(username):
    try:
        # Get page data
        page = mongo.db.pages.find_one({'username': username.lower()})
        if not page:
            return jsonify({
                "success": False,
                "error": {
                    "code": "PAGE_NOT_FOUND",
                    "message": "Page not found"
                }
            }), 404

        # Get metrics
        followers = page.get('followers', 0)
        likes = page.get('likes', 0)

        # Generate AI summary
        ai_service = AISummaryService()
        summary = await ai_service.generate_summary(page)
        
        if not summary:
            return jsonify({
                "success": False,
                "error": {
                    "code": "SUMMARY_GENERATION_FAILED",
                    "message": "Failed to generate summary"
                }
            }), 500

        # Update page with summary
        mongo.db.pages.update_one(
            {'username': username.lower()},
            {
                '$set': {
                    'ai_summary': summary,
                    'updated_at': datetime.utcnow()
                }
            }
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
            },
            "meta": {
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": str(ObjectId())
            }
        })

    except Exception as e:
        print(f"Error in generate_page_summary: {str(e)}")
        return jsonify({
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": str(e)
            }
        }), 500

# Error handlers
@pages_bp.errorhandler(404)
def not_found_error(error):
    return jsonify({
        "success": False,
        "error": {
            "code": "NOT_FOUND",
            "message": "Resource not found",
            "details": str(error)
        }
    }), 404

@pages_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": {
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An internal server error occurred",
            "details": str(error)
        }
    }), 500