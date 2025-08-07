from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
import os
from datetime import datetime

app = Flask(__name__)

# Configuration
app.config['DEBUG'] = os.environ.get('DEBUG', 'True').lower() == 'true'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'puppetron-secret-key')

# StoryTRON API configuration
STORYTRON_BASE_URL = os.environ.get('STORYTRON_URL', 'http://localhost:5000')

def call_storytron_api(endpoint, method='GET', data=None):
    """Helper function to call StoryTRON API"""
    try:
        url = f"{STORYTRON_BASE_URL}{endpoint}"
        if method == 'GET':
            response = requests.get(url, timeout=5)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=5)
        else:
            return None

        if response.status_code == 200:
            return response.json()
        else:
            return None
    except requests.exceptions.RequestException:
        return None

@app.route('/')
def dashboard():
    """Main dashboard - shows system status and active agent"""
    # Get system status from StoryTRON
    status = call_storytron_api('/')
    agents = call_storytron_api('/agents')

    return render_template('dashboard.html',
                         status=status,
                         agents=agents,
                         timestamp=datetime.now().strftime('%H:%M:%S'))

@app.route('/agents')
def agents_page():
    """Agents management page"""
    agents = call_storytron_api('/agents')
    return render_template('agents.html', agents=agents)

@app.route('/switch-agent', methods=['POST'])
def switch_agent():
    """Switch active agent"""
    agent_id = request.form.get('agent_id')
    if agent_id:
        result = call_storytron_api(f'/agents/{agent_id}/activate', method='POST')
        if result:
            return redirect(url_for('dashboard'))

    return redirect(url_for('agents_page'))

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    """Chat interface for testing"""
    if request.method == 'POST':
        message = request.form.get('message')
        if message:
            response = call_storytron_api('/chat', method='POST', data={'message': message})
            return render_template('chat.html', user_message=message, bot_response=response)

    return render_template('chat.html')

@app.route('/api/status')
def api_status():
    """API endpoint for real-time status updates"""
    status = call_storytron_api('/')
    return jsonify(status) if status else jsonify({'error': 'StoryTRON not available'})

@app.route('/send-message', methods=['POST'])
def send_message():
    """Send message to pomo device (future implementation)"""
    data = request.get_json()
    message = data.get('message', '')

    # TODO: Implement sending message to pomo device
    return jsonify({
        'success': True,
        'message': f'Message "{message}" would be sent to pomo device',
        'timestamp': datetime.now().isoformat()
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', error_code=404, error_message='Page not found'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error_code=500, error_message='Internal server error'), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    host = os.environ.get('HOST', '0.0.0.0')  # 0.0.0.0 for phone access

    app.run(
        host=host,
        port=port,
        debug=app.config['DEBUG']
    )
