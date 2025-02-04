# app/routes/page_routes.py

from flask import Blueprint, jsonify, request
from app import mongo
from app.services.scraper import FacebookScraper
from app.models.page import Page
from bson import ObjectId

pages_bp = Blueprint('pages', __name__, url_prefix='/api')

# Health Check
@pages_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'API is running'
    })

# Get Page by Username
@pages_bp.route('/page/<username>', methods=['GET'])
def get_page(username):
    try:
        # Check if page exists in DB
        page = mongo.db.pages.find_one({'username': username})
        
        if not page:
            # Scrape page if not in DB
            scraper = FacebookScraper()
            page_data = scraper.scrape_page(username)
            
            if page_data:
                page_dict = page_data.to_dict()
                mongo.db.pages.insert_one(page_dict)
                return jsonify(page_dict)
            return jsonify({'error': 'Page not found'}), 404
        
        return jsonify(page)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get Pages with Filters
@pages_bp.route('/pages', methods=['GET'])
def get_pages():
    try:
        # Get query parameters
        follower_min = int(request.args.get('follower_min', 0))
        follower_max = int(request.args.get('follower_max', float('inf')))
        category = request.args.get('category')
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
            query['category'] = category

        # Execute query with pagination
        total = mongo.db.pages.count_documents(query)
        pages = list(mongo.db.pages.find(query)
                    .skip((page-1)*per_page)
                    .limit(per_page))
        
        return jsonify({
            'pages': pages,
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': (total + per_page - 1) // per_page
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get Page Posts
@pages_bp.route('/page/<username>/posts', methods=['GET'])
def get_page_posts(username):
    try:
        page = mongo.db.pages.find_one({'username': username})
        if not page:
            return jsonify({'error': 'Page not found'}), 404

        limit = int(request.args.get('limit', 10))
        posts = list(mongo.db.posts.find({'page_id': str(page['_id'])})
                    .limit(limit))
        
        return jsonify({
            'posts': posts,
            'total': len(posts)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Search Pages
@pages_bp.route('/search', methods=['GET'])
def search_pages():
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
        
        return jsonify({
            'pages': pages,
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': (total + per_page - 1) // per_page
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500