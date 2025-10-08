#!/usr/bin/env python3
"""
Hotel Management Ratings API
Fetches ratings data from hotel_management database
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# MySQL Database Configuration - Remote Hotel Database
MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST', '192.168.1.12'),  # IP address from environment variable
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),  # Password from environment variable
    'database': os.getenv('MYSQL_DATABASE', 'hotel_management'),
    'port': int(os.getenv('MYSQL_PORT', '3306')),
    'charset': 'utf8mb4',
    'autocommit': True
}

def get_database_connection():
    """Create and return MySQL database connection"""
    try:
        import mysql.connector
        from mysql.connector import Error
        
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        if connection.is_connected():
            return connection
        else:
            print("Failed to connect to MySQL database")
            return None
    except Error as e:
        print(f"Error connecting to MySQL Database: {e}")
        return None
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def format_datetime(dt):
    """Format datetime for JSON serialization"""
    if isinstance(dt, datetime):
        return dt.isoformat()
    return dt

@app.route('/api/hotel-ratings', methods=['GET'])
def get_hotel_ratings():
    """Get all ratings from eatnrun_rating table"""
    try:
        connection = get_database_connection()
        if not connection:
            return jsonify({
                'success': False,
                'error': 'Database connection failed',
                'data': []
            }), 500

        cursor = connection.cursor(dictionary=True)
        
        # Query to get ratings with order details (MySQL compatible)
        query = """
        SELECT 
            er.id,
            er.rating,
            er.comment,
            er.created_at,
            er.updated_at,
            er.order_id,
            'Hotel Guest' as customer_name,
            'hotel@example.com' as customer_email,
            'N/A' as customer_phone
        FROM eatnrun_rating er
        ORDER BY er.created_at DESC
        """
        
        cursor.execute(query)
        ratings = cursor.fetchall()
        
        # Format the data
        formatted_ratings = []
        for rating in ratings:
            formatted_rating = {
                'id': rating['id'],
                'rating': rating['rating'],
                'comment': rating['comment'],
                'created_at': format_datetime(rating['created_at']),
                'updated_at': format_datetime(rating['updated_at']),
                'order_id': rating['order_id'],
                'customer': {
                    'name': rating['customer_name'],
                    'email': rating['customer_email'],
                    'phone': rating['customer_phone']
                }
            }
            formatted_ratings.append(formatted_rating)
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'success': True,
            'data': formatted_ratings,
            'total_count': len(formatted_ratings),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'data': []
        }), 500

@app.route('/api/hotel-ratings/stats', methods=['GET'])
def get_hotel_ratings_stats():
    """Get statistics for hotel ratings"""
    try:
        connection = get_database_connection()
        if not connection:
            return jsonify({
                'success': False,
                'error': 'Database connection failed',
                'stats': {}
            }), 500

        cursor = connection.cursor()
        
        # Get total ratings
        cursor.execute("SELECT COUNT(*) FROM eatnrun_rating")
        total_ratings = cursor.fetchone()[0]
        
        # Get average rating
        cursor.execute("SELECT AVG(rating) FROM eatnrun_rating")
        avg_rating = cursor.fetchone()[0]
        
        # Get rating distribution
        cursor.execute("""
            SELECT rating, COUNT(*) as count 
            FROM eatnrun_rating 
            GROUP BY rating 
            ORDER BY rating DESC
        """)
        rating_distribution = cursor.fetchall()
        
        # Get recent ratings (last 7 days) - MySQL compatible
        cursor.execute("""
            SELECT COUNT(*) 
            FROM eatnrun_rating 
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
        """)
        recent_ratings = cursor.fetchone()[0]
        
        cursor.close()
        connection.close()
        
        stats = {
            'total_ratings': total_ratings,
            'average_rating': float(avg_rating) if avg_rating else 0,
            'recent_ratings': recent_ratings,
            'rating_distribution': {str(r[0]): r[1] for r in rating_distribution}
        }
        
        return jsonify({
            'success': True,
            'stats': stats,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'stats': {}
        }), 500

@app.route('/api/hotel-ratings/<int:rating_id>', methods=['GET'])
def get_hotel_rating_detail(rating_id):
    """Get specific rating details"""
    try:
        connection = get_database_connection()
        if not connection:
            return jsonify({
                'success': False,
                'error': 'Database connection failed',
                'data': {}
            }), 500

        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT 
            er.id,
            er.rating,
            er.comment,
            er.created_at,
            er.updated_at,
            er.order_id,
            'Hotel Guest' as customer_name,
            'hotel@example.com' as customer_email,
            'N/A' as customer_phone
        FROM eatnrun_rating er
        WHERE er.id = %s
        """
        
        cursor.execute(query, (rating_id,))
        rating = cursor.fetchone()
        
        if not rating:
            return jsonify({
                'success': False,
                'error': 'Rating not found',
                'data': {}
            }), 404
        
        formatted_rating = {
            'id': rating['id'],
            'rating': rating['rating'],
            'comment': rating['comment'],
            'created_at': format_datetime(rating['created_at']),
            'updated_at': format_datetime(rating['updated_at']),
            'order_id': rating['order_id'],
            'customer': {
                'name': rating['customer_name'],
                'email': rating['customer_email'],
                'phone': rating['customer_phone']
            }
        }
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'success': True,
            'data': formatted_rating,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'data': {}
        }), 500

@app.route('/api/hotel-ratings/search', methods=['GET'])
def search_hotel_ratings():
    """Search ratings by various criteria"""
    try:
        connection = get_database_connection()
        if not connection:
            return jsonify({
                'success': False,
                'error': 'Database connection failed',
                'data': []
            }), 500

        cursor = connection.cursor(dictionary=True)
        
        # Get search parameters
        rating = request.args.get('rating', type=int)
        customer_name = request.args.get('customer_name', '')
        date_from = request.args.get('date_from', '')
        date_to = request.args.get('date_to', '')
        limit = request.args.get('limit', 50, type=int)
        
        # Build query with conditions
        query = """
        SELECT 
            er.id,
            er.rating,
            er.comment,
            er.created_at,
            er.updated_at,
            er.order_id,
            'Hotel Guest' as customer_name,
            'hotel@example.com' as customer_email,
            'N/A' as customer_phone
        FROM eatnrun_rating er
        WHERE 1=1
        """
        
        params = []
        
        if rating:
            query += " AND er.rating = %s"
            params.append(rating)
        
        if customer_name:
            query += " AND er.comment LIKE %s"
            params.append(f"%{customer_name}%")
        
        if date_from:
            query += " AND er.created_at >= %s"
            params.append(date_from)
        
        if date_to:
            query += " AND er.created_at <= %s"
            params.append(date_to)
        
        query += " ORDER BY er.created_at DESC LIMIT %s"
        params.append(limit)
        
        cursor.execute(query, params)
        ratings = cursor.fetchall()
        
        # Format the data
        formatted_ratings = []
        for rating in ratings:
            formatted_rating = {
                'id': rating['id'],
                'rating': rating['rating'],
                'comment': rating['comment'],
                'created_at': format_datetime(rating['created_at']),
                'updated_at': format_datetime(rating['updated_at']),
                'order_id': rating['order_id'],
                'customer': {
                    'name': rating['customer_name'],
                    'email': rating['customer_email'],
                    'phone': rating['customer_phone']
                }
            }
            formatted_ratings.append(formatted_rating)
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'success': True,
            'data': formatted_ratings,
            'total_count': len(formatted_ratings),
            'search_params': {
                'rating': rating,
                'customer_name': customer_name,
                'date_from': date_from,
                'date_to': date_to,
                'limit': limit
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'data': []
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        connection = get_database_connection()
        if connection:
            connection.close()
            status = 'healthy'
        else:
            status = 'unhealthy'
    except:
        status = 'unhealthy'
    
    return jsonify({
        'status': status,
        'timestamp': datetime.now().isoformat(),
        'service': 'Hotel Ratings API'
    })

if __name__ == '__main__':
    # Create .env file if it doesn't exist
    env_file = '.env'
    if not os.path.exists(env_file):
        with open(env_file, 'w') as f:
            f.write("""# Database Configuration
DB_HOST=localhost
DB_USER=root
DB_PASS=
DB_NAME=hotel_management
DB_PORT=3306
""")
        print(f"Created {env_file} file. Please update with your database credentials.")
    
    print("Starting Hotel Ratings API...")
    print("Available endpoints:")
    print("  GET /api/hotel-ratings - Get all ratings")
    print("  GET /api/hotel-ratings/stats - Get rating statistics")
    print("  GET /api/hotel-ratings/<id> - Get specific rating")
    print("  GET /api/hotel-ratings/search - Search ratings")
    print("  GET /api/health - Health check")
    print("\nTo run with your preferred command:")
    print("  flask run --host=0.0.0.0 --port=5000")
    print("\nOr run directly:")
    print("  python hotel_ratings_api.py")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
