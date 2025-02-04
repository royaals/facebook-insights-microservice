from flask import Blueprint, jsonify, request
from app import mongo
from app.services.scraper import FacebookScraper
from app.services.ai_summary import AISummary
from app.utils.helpers import format_page_response
from datetime import datetime
from bson import ObjectId

pages_bp = Blueprint('pages', __name__, url_prefix='/api')

@pages_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "API is running",
        "server_time": datetime.utcnow().isoformat(),
        "database_status": "connected"
    })

@pages_bp.route('/page/<username>', methods=['GET'])
async def get_page(username):
    """Get page details by username"""
    try:
        # Check if page exists in DB
        page = mongo.db.pages.find_one({'username': username.lower()})
        
        if not page:
            # Scrape page if not in DB
            scraper = FacebookScraper()
            page_data = await scraper.scrape_page(username)
            
            if page_data:
                # Generate AI summary
                ai = AISummary()
                summary = ai.generate_page_summary(page_data.to_dict())
                if summary:
                    page_data.ai_summary = summary

                # Store in DB
                page_dict = page_data.to_dict()
                mongo.db.pages.insert_one(page_dict)
                
                # Format response
                response_data = format_page_response(page_dict)
                return jsonify({
                    "success": True,
                    "data": response_data
                })
            
            return jsonify({
                "success": False,
                "error": {
                    "code": "PAGE_NOT_FOUND",
                    "message": "Page not found"
                }
            }), 404
        
        # Format response for existing page
        response_data = format_page_response(page)
        return jsonify({
            "success": True,
            "data": response_data
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": str(e)
            }
        }), 500

@pages_bp.route('/pages', methods=['GET'])
def get_pages():
    """Get pages with filters"""
    try:
        # Get query parameters
        follower_min = int(request.args.get('follower_min', 0))
        follower_max = int(request.args.get('follower_max', float('inf')))
        category = request.args.get('category')
        name = request.args.get('name')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))

        # Build query
        query = {
            'followers_count': {
                '$gte': follower_min,
                '$lte': follower_max
            }
        }
        if category:
            query['category'] = {'$regex': category, '$options': 'i'}
        if name:
            query['name'] = {'$regex': name, '$options': 'i'}

        # Execute query with pagination
        total = mongo.db.pages.count_documents(query)
        pages = list(mongo.db.pages.find(query)
                    .skip((page-1)*per_page)
                    .limit(per_page))
        
        # Format response
        response_data = [format_page_response(p) for p in pages]
        
        return jsonify({
            "success": True,
            "data": {
                "pages": response_data,
                "pagination": {
                    "current_page": page,
                    "per_page": per_page,
                    "total_items": total,
                    "total_pages": (total + per_page - 1) // per_page
                }
            },
            "meta": {
                "filters_applied": {
                    "follower_min": follower_min,
                    "follower_max": follower_max,
                    "category": category,
                    "name": name
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": str(e)
            }
        }), 500

@pages_bp.route('/page/<username>/posts', methods=['GET'])
def get_page_posts(username):
    """Get posts for a specific page"""
    try:
        page = mongo.db.pages.find_one({'username': username.lower()})
        if not page:
            return jsonify({
                "success": False,
                "error": {
                    "code": "PAGE_NOT_FOUND",
                    "message": "Page not found"
                }
            }), 404

        limit = int(request.args.get('limit', 15))
        page_num = int(request.args.get('page', 1))

        posts = list(mongo.db.posts.find({'page_id': str(page['_id'])})
                    .sort('created_at', -1)
                    .skip((page_num-1)*limit)
                    .limit(limit))
        
        total = mongo.db.posts.count_documents({'page_id': str(page['_id'])})
        
        return jsonify({
            "success": True,
            "data": {
                "posts": posts,
                "pagination": {
                    "current_page": page_num,
                    "per_page": limit,
                    "total_items": total,
                    "total_pages": (total + limit - 1) // limit
                }
            }
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": str(e)
            }
        }), 500

@pages_bp.route('/search', methods=['GET'])
def search_pages():
    """Search pages by name or category"""
    try:
        query = request.args.get('q', '')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))

        # Build search query
        search_query = {
            '$or': [
                {'name': {'$regex': query, '$options': 'i'}},
                {'category': {'$regex': query, '$options': 'i'}}
            ]
        }

        # Execute query with pagination
        total = mongo.db.pages.count_documents(search_query)
        pages = list(mongo.db.pages.find(search_query)
                    .skip((page-1)*per_page)
                    .limit(per_page))
        
        # Format response
        response_data = [format_page_response(p) for p in pages]
        
        return jsonify({
            "success": True,
            "data": {
                "results": response_data,
                "pagination": {
                    "current_page": page,
                    "per_page": per_page,
                    "total_items": total,
                    "total_pages": (total + per_page - 1) // per_page
                }
            },
            "meta": {
                "search_query": query,
                "timestamp": datetime.utcnow().isoformat()
            }
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": str(e)
            }
        }), 500