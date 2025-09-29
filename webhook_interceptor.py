import requests
import json
from flask import Flask, request, jsonify
import threading
import time

"""
🔄 Webhook Redirector
Detta script interceptar alla webhook-meddelanden och skickar dem till din dashboard
"""

app = Flask(__name__)

# Original Discord webhook URLs (från servern)
ORIGINAL_WEBHOOKS = {
    'vorp_report': [
        'https://discord.com/api/webhooks/1277275776542343250/ZpyObOyVQOYaTNKHAYnX68xqJc5RNWM2MvOpz0cWa-CqnYlJLfLCJ3q5gqj4sD8_8NeD',
        'https://discord.com/api/webhooks/1277275889952460961/u5IVYs33H2sEdPTk7AyWITX5UtEa6bJFI8rGN0a5d0EGKXxZBGMbwkLDDaUTwxIJSGJf',
        'https://discord.com/api/webhooks/1277275948731990136/1yrSvKV1w8cVnJL4zNv3HkTXIj5qe-EhAbQDjKXJVSNb8aZ7a1qK5cHIpGtYgX0ZMN6Q'
    ],
    'dsadmin': [
        'https://discord.com/api/webhooks/1269993302419095594/YOUR_DSADMIN_TOKEN_HERE'
    ]
}

# Din dashboard URL
DASHBOARD_URL = "http://localhost:5000"

@app.route('/webhook/vorp_report/<path:webhook_id>', methods=['POST'])
def intercept_vorp_report(webhook_id):
    """Interceptar vorp_report webhooks"""
    data = request.json or request.form.to_dict()
    
    print(f"📨 Intercepted vorp_report webhook: {webhook_id}")
    print(f"📄 Data: {json.dumps(data, indent=2)}")
    
    # Skicka till dashboard
    try:
        requests.post(f"{DASHBOARD_URL}/webhook/vorp_report", 
                     json=data, 
                     timeout=5)
    except Exception as e:
        print(f"❌ Failed to send to dashboard: {e}")
    
    # Skicka till original Discord webhook (valfritt)
    forward_to_discord('vorp_report', data)
    
    return jsonify({"status": "intercepted"})

@app.route('/webhook/dsadmin/<path:webhook_id>', methods=['POST'])
def intercept_dsadmin(webhook_id):
    """Interceptar dsAdminMenu webhooks"""
    data = request.json or request.form.to_dict()
    
    print(f"🛡️ Intercepted dsadmin webhook: {webhook_id}")
    print(f"📄 Data: {json.dumps(data, indent=2)}")
    
    # Skicka till dashboard
    try:
        requests.post(f"{DASHBOARD_URL}/webhook/dsadmin", 
                     json=data, 
                     timeout=5)
    except Exception as e:
        print(f"❌ Failed to send to dashboard: {e}")
    
    # Skicka till original Discord webhook (valfritt)
    forward_to_discord('dsadmin', data)
    
    return jsonify({"status": "intercepted"})

@app.route('/webhook/<path:webhook_path>', methods=['POST'])
def intercept_generic(webhook_path):
    """Fånga alla andra webhooks"""
    data = request.json or request.form.to_dict()
    
    print(f"🌐 Intercepted generic webhook: {webhook_path}")
    print(f"📄 Data: {json.dumps(data, indent=2)}")
    
    # Skicka till dashboard
    try:
        requests.post(f"{DASHBOARD_URL}/webhook/catch_all", 
                     json=data, 
                     timeout=5)
    except Exception as e:
        print(f"❌ Failed to send to dashboard: {e}")
    
    return jsonify({"status": "intercepted"})

def forward_to_discord(webhook_type, data):
    """Vidarebefordra till original Discord webhooks (valfritt)"""
    if webhook_type not in ORIGINAL_WEBHOOKS:
        return
    
    for webhook_url in ORIGINAL_WEBHOOKS[webhook_type]:
        try:
            response = requests.post(webhook_url, json=data, timeout=10)
            if response.status_code == 200:
                print(f"✅ Forwarded to Discord: {webhook_url[:50]}...")
            else:
                print(f"⚠️ Discord forward failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Discord forward error: {e}")

if __name__ == '__main__':
    print("🔄 Starting Webhook Redirector...")
    print("📡 Listening on: http://localhost:8080")
    print("🎯 Dashboard URL: http://localhost:5000")
    print("\n🔧 To use this, replace server webhook URLs with:")
    print("   - vorp_report: http://YOUR_IP:8080/webhook/vorp_report/ID")
    print("   - dsadmin: http://YOUR_IP:8080/webhook/dsadmin/ID")
    print("   - generic: http://YOUR_IP:8080/webhook/ANYTHING")
    
    app.run(host='0.0.0.0', port=8080, debug=True)