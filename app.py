from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import json
import datetime
import sqlite3
import threading
from collections import defaultdict

app = Flask(__name__)
app.config['SECRET_KEY'] = 'fivem_monitor_secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# Database setup
def init_db():
    conn = sqlite3.connect('fivem_logs.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp TEXT,
                  webhook_source TEXT,
                  message_type TEXT,
                  content TEXT,
                  player_id TEXT,
                  raw_data TEXT)''')
    conn.commit()
    conn.close()

# Initialize database
init_db()

# Global storage for real-time data
live_data = {
    'online_players': [],
    'recent_actions': [],
    'admin_actions': [],
    'chat_messages': [],
    'server_stats': {},
    'alerts': []
}

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/webhook/vorp_report', methods=['POST'])
def vorp_report_webhook():
    """Intercept vorp_report webhook data"""
    data = request.json
    
    log_entry = {
        'timestamp': datetime.datetime.now().isoformat(),
        'webhook_source': 'vorp_report',
        'message_type': 'report',
        'content': data.get('content', ''),
        'raw_data': json.dumps(data)
    }
    
    # Save to database
    save_log(log_entry)
    
    # Emit to dashboard in real-time
    socketio.emit('new_log', log_entry)
    
    # Parse for specific information
    parse_report_data(data)
    
    return jsonify({"status": "received"})

@app.route('/webhook/dsadmin', methods=['POST'])
def dsadmin_webhook():
    """Intercept dsAdminMenu webhook data"""
    data = request.json
    
    log_entry = {
        'timestamp': datetime.datetime.now().isoformat(),
        'webhook_source': 'dsadmin',
        'message_type': 'admin_action',
        'content': data.get('content', ''),
        'raw_data': json.dumps(data)
    }
    
    # Save to database
    save_log(log_entry)
    
    # Emit to dashboard
    socketio.emit('new_admin_action', log_entry)
    
    # Parse admin actions
    parse_admin_data(data)
    
    return jsonify({"status": "received"})

@app.route('/webhook/catch_all', methods=['POST'])
def catch_all_webhook():
    """Catch all other webhook traffic"""
    data = request.json
    
    log_entry = {
        'timestamp': datetime.datetime.now().isoformat(),
        'webhook_source': 'unknown',
        'message_type': 'general',
        'content': data.get('content', ''),
        'raw_data': json.dumps(data)
    }
    
    # Save to database
    save_log(log_entry)
    
    # Emit to dashboard
    socketio.emit('new_general_log', log_entry)
    
    return jsonify({"status": "received"})

def save_log(log_entry):
    """Save log entry to database"""
    conn = sqlite3.connect('fivem_logs.db')
    c = conn.cursor()
    c.execute('''INSERT INTO logs (timestamp, webhook_source, message_type, content, raw_data)
                 VALUES (?, ?, ?, ?, ?)''', 
              (log_entry['timestamp'], log_entry['webhook_source'], 
               log_entry['message_type'], log_entry['content'], log_entry['raw_data']))
    conn.commit()
    conn.close()

def parse_report_data(data):
    """Parse vorp_report data for useful information"""
    content = data.get('content', '')
    embeds = data.get('embeds', [])
    
    # Look for player reports
    if 'report' in content.lower():
        live_data['recent_actions'].append({
            'type': 'player_report',
            'timestamp': datetime.datetime.now().isoformat(),
            'content': content,
            'embeds': embeds
        })
        
        # Emit alert if it looks suspicious
        if any(keyword in content.lower() for keyword in ['hack', 'cheat', 'exploit', 'sql']):
            alert = {
                'type': 'suspicious_report',
                'timestamp': datetime.datetime.now().isoformat(),
                'content': content,
                'severity': 'high'
            }
            live_data['alerts'].append(alert)
            socketio.emit('alert', alert)

def parse_admin_data(data):
    """Parse admin action data"""
    content = data.get('content', '')
    embeds = data.get('embeds', [])
    
    # Track admin actions
    admin_action = {
        'timestamp': datetime.datetime.now().isoformat(),
        'action': content,
        'embeds': embeds
    }
    
    live_data['admin_actions'].append(admin_action)
    
    # Keep only last 100 actions
    if len(live_data['admin_actions']) > 100:
        live_data['admin_actions'] = live_data['admin_actions'][-100:]

@app.route('/api/stats')
def get_stats():
    """Get server statistics"""
    conn = sqlite3.connect('fivem_logs.db')
    c = conn.cursor()
    
    # Get log counts by type
    c.execute('SELECT message_type, COUNT(*) FROM logs GROUP BY message_type')
    type_counts = dict(c.fetchall())
    
    # Get recent activity (last 24 hours)
    c.execute('''SELECT timestamp, message_type, content FROM logs 
                 WHERE datetime(timestamp) > datetime('now', '-1 day')
                 ORDER BY timestamp DESC LIMIT 50''')
    recent_activity = c.fetchall()
    
    conn.close()
    
    return jsonify({
        'type_counts': type_counts,
        'recent_activity': recent_activity,
        'live_data': live_data
    })

@app.route('/api/search')
def search_logs():
    """Search logs by keyword"""
    query = request.args.get('q', '')
    
    if not query:
        return jsonify([])
    
    conn = sqlite3.connect('fivem_logs.db')
    c = conn.cursor()
    c.execute('''SELECT timestamp, webhook_source, message_type, content 
                 FROM logs WHERE content LIKE ? 
                 ORDER BY timestamp DESC LIMIT 100''', 
              (f'%{query}%',))
    results = c.fetchall()
    conn.close()
    
    return jsonify(results)

@socketio.on('connect')
def handle_connect():
    emit('connected', {'data': 'Connected to FiveM Monitor'})

if __name__ == '__main__':
    print("🖥️  Starting FiveM Server Monitor Dashboard...")
    print("📊 Dashboard: http://localhost:5000")
    print("🔗 Webhook endpoints:")
    print("   - http://localhost:5000/webhook/vorp_report")
    print("   - http://localhost:5000/webhook/dsadmin") 
    print("   - http://localhost:5000/webhook/catch_all")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)