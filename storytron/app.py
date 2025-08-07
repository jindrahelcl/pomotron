from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Configuration
app.config['DEBUG'] = os.environ.get('DEBUG', 'False').lower() == 'true'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Global state for active agent
active_agent_id = "default"  # There's always one active agent

# Health check / keep-alive endpoint
@app.route('/')
def keep_alive():
    return jsonify({
        'status': 'alive',
        'service': 'StoryTRON',
        'active_agent': active_agent_id
    })

@app.route('/agents', methods=['GET'])
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

@app.route('/agents/<agent_id>/activate', methods=['POST'])
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

@app.route('/chat', methods=['POST'])
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
        'timestamp': None  # TODO: Add timestamp
    })

# Error handlers
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