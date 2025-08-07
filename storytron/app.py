from flask import Flask, request, jsonify, render_template, redirect, url_for
import os
from datetime import datetime

app = Flask(__name__)

# Configuration
app.config['DEBUG'] = os.environ.get('DEBUG', 'False').lower() == 'true'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Global state for active agent
active_agent_id = "default"  # There's always one active agent

# Health check / keep-alive endpoint (API)
@app.route('/api')
def keep_alive_api():
    return jsonify({
        'status': 'alive',
        'service': 'StoryTRON',
        'active_agent': active_agent_id
    })

# Web frontend routes
@app.route('/')
def dashboard():
    """Main web dashboard"""
    # Get available agents
    available_agents = [
        {"id": "default", "name": "Default Agent", "description": "Basic conversational agent"},
        {"id": "helper", "name": "Helper Agent", "description": "Task assistance agent"},
        {"id": "creative", "name": "Creative Agent", "description": "Creative writing agent"}
    ]

    status = {
        'status': 'alive',
        'service': 'StoryTRON',
        'active_agent': active_agent_id
    }

    return render_template('dashboard.html',
                         status=status,
                         agents={'agents': available_agents, 'active_agent': active_agent_id},
                         timestamp=datetime.now().strftime('%H:%M:%S'))

@app.route('/web/agents')
def web_agents():
    """Web agents management page"""
    available_agents = [
        {"id": "default", "name": "Default Agent", "description": "Basic conversational agent"},
        {"id": "helper", "name": "Helper Agent", "description": "Task assistance agent"},
        {"id": "creative", "name": "Creative Agent", "description": "Creative writing agent"}
    ]

    return render_template('agents.html',
                         agents={'agents': available_agents, 'active_agent': active_agent_id})

@app.route('/web/chat', methods=['GET', 'POST'])
def web_chat():
    """Web chat interface"""
    if request.method == 'POST':
        message = request.form.get('message')
        if message:
            # Simulate chat response (same logic as API endpoint)
            response = {
                'active_agent': active_agent_id,
                'user_message': message,
                'agent_response': f'Response from {active_agent_id}: This is a placeholder response.',
                'timestamp': datetime.now().isoformat()
            }
            return render_template('chat.html', user_message=message, bot_response=response)

    return render_template('chat.html')

@app.route('/switch-agent', methods=['POST'])
def web_switch_agent():
    """Web agent switching"""
    agent_id = request.form.get('agent_id')
    if agent_id:
        global active_agent_id
        active_agent_id = agent_id
        return redirect(url_for('dashboard'))
    return redirect(url_for('web_agents'))

@app.route('/api/agents', methods=['GET'])
def list_agents():
    """List all available GPT agents including the active one"""
    # TODO: Implement actual agent listing logic
    available_agents = [
        {"id": "default", "name": "Default Agent", "description": "Basic conversational agent"},
        {"id": "helper", "name": "Helper Agent", "description": "Task assistance agent"},
        {"id": "creative", "name": "Creative Agent", "description": "Creative writing agent"}
    ]

    return jsonify({
        'agents': available_agents,
        'active_agent': active_agent_id
    })

@app.route('/api/agents/<agent_id>/activate', methods=['POST'])
def switch_agent(agent_id):
    """Switch to a different agent by ID"""
    global active_agent_id

    # TODO: Validate that agent_id exists
    # For now, just accept any agent_id
    active_agent_id = agent_id

    return jsonify({
        'message': f'Switched to agent: {agent_id}',
        'active_agent': active_agent_id
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """Send a message to the active agent"""
    data = request.get_json()

    if not data or 'message' not in data:
        return jsonify({
            'error': 'Message is required'
        }), 400

    message = data.get('message', '')

    # TODO: Implement actual chat with the active GPT agent
    return jsonify({
        'active_agent': active_agent_id,
        'user_message': message,
        'agent_response': f'Response from {active_agent_id}: This is a placeholder response.',
        'timestamp': datetime.now().isoformat()
    })# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Not found',
        'message': 'The requested resource was not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'message': 'An internal error occurred'
    }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')  # 0.0.0.0 for public IP access

    app.run(
        host=host,
        port=port,
        debug=app.config['DEBUG']
    )