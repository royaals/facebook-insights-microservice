# Facebook Insights API

A powerful Flask-based API that scrapes and analyzes Facebook pages to provide detailed insights, engagement metrics, and AI-powered summaries.

## Description

Facebook Insights API is a microservice that allows users to fetch and analyze Facebook pages by their usernames. The service scrapes page data, stores it in MongoDB, and provides various endpoints for retrieving page details, posts, and AI-generated summaries. It's designed to help businesses and analysts understand Facebook page performance and engagement metrics.

## Features

### Core Features
- 🔍 Real-time Facebook page scraping
- 📊 Detailed page analytics and metrics
- 💾 MongoDB data persistence
- 🤖 AI-powered page analysis and recommendations
- 📱 REST API endpoints

## Tech Stack

### Backend
- Python 3.8+
- Flask (Web Framework)
- Selenium (Web Scraping)
- BeautifulSoup4 (HTML Parsing)
- MongoDB (Database)
- OpenAI GPT-3.5 (AI Analysis)

### Storage
- MongoDB (Data Storage)
- S3 (Image Storage)

## Installation

### Prerequisites
- Python 3.8 or higher
- MongoDB
- Chrome/Chromium browser (for Selenium)
- OpenAI API key
- Docker

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/royaals/facebook-insights-microservice.git
cd facebook-insights-microservice
```

2. **Create and activate virtual environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
Create a `.env` file in the root directory

5. **Initialize MongoDB**
```bash
# Start MongoDB using Docker
docker pull mongo

docker run -d --name mongodb -p 27017:27017 -v mongo-data:/data/db mongo
```

6. **Run the application**
```bash
flask run 
```

The API will be available at `http://localhost:5000`

## API Endpoints

### Page Details
```http
GET /api/pages/{username}
```
Fetches detailed information about a Facebook page.

### Page Summary
```http
POST /api/pages/{username}/summary
```
Generates AI-powered analysis and recommendations.

### Example Response
```json
{
    "success": true,
    "data": {
        "page_name": "Example Page",
        "category": "Technology Company",
        "stats": {
            "followers": 1000000,
            "likes": 950000,
            "followers_formatted": "1,000,000",
            "likes_formatted": "950,000"
        },
        "ai_summary": {
            "summary": "Detailed AI analysis...",
            "page_type": "Technology Brand",
            "engagement_level": "Very High",
            "content_strategy": "Product launches, innovation stories"
        }
    }
}
```

## Usage

1. **Get Page Details**
```bash
curl http://localhost:5000/api/pages/facebook
```

2. **Generate AI Summary**
```bash
curl -X POST http://localhost:5000/api/pages/facebook/summary
```

## Error Handling

The API returns appropriate HTTP status codes and error messages:
- 200: Success
- 404: Page not found
- 500: Server error

Example error response:
```json
{
    "success": false,
    "error": "Page not found"
}
```

