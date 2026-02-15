from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from database import Database
from ai_generator import AIGenerator
from datetime import datetime
import mysql.connector

app = Flask(__name__)
CORS(app)

# Initialize database and AI generator
db = Database()
ai_generator = AIGenerator()

# ==================== Routes ====================

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

# ==================== Event Management APIs ====================

@app.route('/api/events', methods=['GET'])
def get_events():
    """Get all events"""
    try:
        conn = db.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM events ORDER BY date DESC")
        events = cursor.fetchall()
        cursor.close()
        
        # Convert date objects to strings
        for event in events:
            if event['date']:
                event['date'] = event['date'].strftime('%Y-%m-%d')
            if event['created_at']:
                event['created_at'] = event['created_at'].isoformat()
            if event['updated_at']:
                event['updated_at'] = event['updated_at'].isoformat()
        
        return jsonify({'success': True, 'events': events}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/events', methods=['POST'])
def create_event():
    """Create a new event"""
    try:
        data = request.json
        required_fields = ['title', 'date']
        
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO events (title, date, location, type, description)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            data['title'],
            data['date'],
            data.get('location', ''),
            data.get('type', ''),
            data.get('description', '')
        ))
        
        event_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        
        return jsonify({'success': True, 'event_id': event_id}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/events/<int:event_id>', methods=['GET'])
def get_event(event_id):
    """Get a specific event"""
    try:
        conn = db.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM events WHERE id = %s", (event_id,))
        event = cursor.fetchone()
        cursor.close()
        
        if not event:
            return jsonify({'success': False, 'error': 'Event not found'}), 404
        
        if event['date']:
            event['date'] = event['date'].strftime('%Y-%m-%d')
        if event['created_at']:
            event['created_at'] = event['created_at'].isoformat()
        if event['updated_at']:
            event['updated_at'] = event['updated_at'].isoformat()
        
        return jsonify({'success': True, 'event': event}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/events/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    """Update an event"""
    try:
        data = request.json
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE events 
            SET title = %s, date = %s, location = %s, type = %s, description = %s
            WHERE id = %s
        """, (
            data.get('title'),
            data.get('date'),
            data.get('location', ''),
            data.get('type', ''),
            data.get('description', ''),
            event_id
        ))
        
        conn.commit()
        cursor.close()
        
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    """Delete an event"""
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM events WHERE id = %s", (event_id,))
        conn.commit()
        cursor.close()
        
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== Post Generation APIs ====================

@app.route('/api/generate-post', methods=['POST'])
def generate_post():
    """Generate a social media post"""
    try:
        data = request.json
        required_fields = ['event_id', 'platform', 'tone']
        
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        # Get event data
        conn = db.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM events WHERE id = %s", (data['event_id'],))
        event = cursor.fetchone()
        cursor.close()
        
        if not event:
            return jsonify({'success': False, 'error': 'Event not found'}), 404
        
        # Convert event date to string
        event_data = {
            'title': event['title'],
            'date': event['date'].strftime('%Y-%m-%d') if event['date'] else '',
            'location': event['location'] or '',
            'type': event['type'] or '',
            'description': event['description'] or ''
        }
        
        # Generate post
        result = ai_generator.generate_post(
            event_data,
            data['platform'],
            data['tone']
        )
        
        # Save generated post to database
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO generated_posts (event_id, platform, tone, content, hashtags, status)
            VALUES (%s, %s, %s, %s, %s, 'draft')
        """, (
            data['event_id'],
            data['platform'],
            data['tone'],
            result['content'],
            result['hashtags']
        ))
        
        post_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        
        return jsonify({
            'success': True,
            'post_id': post_id,
            'content': result['content'],
            'hashtags': result['hashtags']
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/posts', methods=['GET'])
def get_posts():
    """Get all generated posts, optionally filtered by event_id"""
    try:
        event_id = request.args.get('event_id', type=int)
        conn = db.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        if event_id:
            cursor.execute("""
                SELECT gp.*, e.title as event_title 
                FROM generated_posts gp
                JOIN events e ON gp.event_id = e.id
                WHERE gp.event_id = %s
                ORDER BY gp.created_at DESC
            """, (event_id,))
        else:
            cursor.execute("""
                SELECT gp.*, e.title as event_title 
                FROM generated_posts gp
                JOIN events e ON gp.event_id = e.id
                ORDER BY gp.created_at DESC
            """)
        
        posts = cursor.fetchall()
        cursor.close()
        
        # Convert datetime objects to strings
        for post in posts:
            if post['created_at']:
                post['created_at'] = post['created_at'].isoformat()
            if post['updated_at']:
                post['updated_at'] = post['updated_at'].isoformat()
        
        return jsonify({'success': True, 'posts': posts}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post_status(post_id):
    """Update post status (draft/approved/posted)"""
    try:
        data = request.json
        status = data.get('status')
        
        if status not in ['draft', 'approved', 'posted']:
            return jsonify({'success': False, 'error': 'Invalid status. Must be: draft, approved, or posted'}), 400
        
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE generated_posts SET status = %s WHERE id = %s", (status, post_id))
        conn.commit()
        cursor.close()
        
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    """Delete a generated post"""
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM generated_posts WHERE id = %s", (post_id,))
        conn.commit()
        cursor.close()
        
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

