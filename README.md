# 🎮 FiveM Webhook Monitor Setup

## Quick Start

1. **Installera dependencies:**
```bash
pip install -r requirements.txt
```

2. **Starta Dashboard:**
```bash
python app.py
```
   - Dashboard: http://localhost:5000

3. **Starta Webhook Interceptor (valfritt):**
```bash
python webhook_interceptor.py
```
   - Interceptor: http://localhost:8080

## 🔧 Konfiguration

### Metod 1: Webhook Replacement (Rekommenderas)
Byt ut webhook URLs i serverns config filer:

**vorp_report/config.lua:**
```lua
Config.Webhook = "http://YOUR_IP:5000/webhook/vorp_report"
Config.SolvedWebhook = "http://YOUR_IP:5000/webhook/vorp_report"
```

**dsAdminMenu config:**
```lua
Config.Webhook = {
    "http://YOUR_IP:5000/webhook/dsadmin"
}
```

### Metod 2: Proxy Interceptor
Använd webhook_interceptor.py som proxy - servern skickar till den, den loggar och vidarebefordrar till Discord.

## 📊 Dashboard Features

### Real-time Monitoring:
- ✅ Live chat och reports
- ✅ Admin actions tracking
- ✅ Server statistics
- ✅ Security alerts
- ✅ Activity timeline
- ✅ Search functionality

### Data Sources:
- 📨 vorp_report webhooks
- 🛡️ dsAdminMenu webhooks  
- 🌐 Generic webhook traffic
- 📊 SQLite database storage

## 🔍 Stealthy Operation

### Transparent Mode:
Dashboard kan köras transparent - loggar allt utan att påverka serverns operation.

### Database Storage:
Alla logs sparas i SQLite för historisk analys.

### Search & Filter:
Sök igenom alla logs med real-time filtering.

## ⚡ Advanced Usage

### SQL Query Integration:
```python
# Lägg till i app.py för att köra SQL queries
@app.route('/api/sql', methods=['POST'])
def execute_sql():
    query = request.json.get('query')
    # Execute against server database
    # Return results to dashboard
```

### Custom Alerts:
```python
# Automatiska alerts för misstänkta aktiviteter
ALERT_KEYWORDS = ['hack', 'cheat', 'exploit', 'sql', 'inject', 'admin']

def check_for_alerts(content):
    if any(keyword in content.lower() for keyword in ALERT_KEYWORDS):
        trigger_alert(content)
```

### Export Functionality:
```python
# Export logs till olika format
@app.route('/api/export/<format>')
def export_logs(format):
    # Export som JSON, CSV, eller TXT
    pass
```

## 🛡️ Security Notes

- Dashboard exponerar ingen server-data utåt
- Endast interceptar webhook traffic
- SQLite database är lokal
- Kan köras på separata maskiner
- Real-time utan att påverka server performance

## 📈 Use Cases

1. **Server Monitoring:** Se all aktivitet i real-time
2. **Security Auditing:** Upptäck misstänkta aktiviteter
3. **Admin Oversight:** Tracka admin actions
4. **Player Reports:** Hantera rapporter effektivt
5. **Performance Analysis:** Analysera server-mönster

Detta ger dig FULL insyn i allt som händer på servern! 🎯