from flask import Flask, request, jsonify, render_template, redirect, url_for
import os
from datetime import datetime
from agents import DefaultAgent, NegativeAgent

app = Flask(__name__)

app.config['DEBUG'] = os.environ.get('DEBUG', 'False').lower() == 'true'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

agents = {
    "default": DefaultAgent(),
    "negative": NegativeAgent()
}
active_agent_id = "default"

@app.route('/')
def index():
    return '', 404

@app.route('/api/keepalive', methods=['POST'])
def keep_alive():
    # TODO: Log the keep-alive, update last-seen timestamp, etc.
    return '', 200

@app.route('/master')
def dashboard():
    available_agents = [agent.to_dict() for agent in agents.values()]

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
    available_agents = [agent.to_dict() for agent in agents.values()]

    return render_template('agents.html',
                         agents={'agents': available_agents, 'active_agent': active_agent_id})

@app.route('/web/chat', methods=['GET', 'POST'])
def web_chat():
    if request.method == 'POST':
        message = request.form.get('message')
        if message:
            agent = agents[active_agent_id]
            agent_response = agent.chat(message)
            response = {
                'active_agent': active_agent_id,
                'user_message': message,
                'agent_response': agent_response,
                'timestamp': datetime.now().isoformat()
            }
            return render_template('chat.html', user_message=message, bot_response=response)

    return render_template('chat.html')

@app.route('/switch-agent', methods=['POST'])
def web_switch_agent():
    agent_id = request.form.get('agent_id')
    if agent_id and agent_id in agents:
        global active_agent_id
        active_agent_id = agent_id
        return redirect(url_for('dashboard'))
    return redirect(url_for('web_agents'))

@app.route('/api/agents', methods=['GET'])
def list_agents():
    available_agents = [agent.to_dict() for agent in agents.values()]

    return jsonify({
        'agents': available_agents,
        'active_agent': active_agent_id
    })

@app.route('/api/agents/<agent_id>/activate', methods=['POST'])
def switch_agent(agent_id):
    global active_agent_id
    if agent_id in agents:
        active_agent_id = agent_id
        return jsonify({
            'message': f'Switched to agent: {agent_id}',
            'active_agent': active_agent_id
        })
    else:
        return jsonify({
            'error': f'Agent {agent_id} not found'
        }), 404

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()

    if not data or 'message' not in data:
        return jsonify({
            'error': 'Message is required'
        }), 400

    message = data.get('message', '')

    agent = agents[active_agent_id]
    agent_response = agent.chat(message)

    return jsonify({
        'active_agent': active_agent_id,
        'user_message': message,
        'agent_response': agent_response,
        'timestamp': datetime.now().isoformat()
    })

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
    host = os.environ.get('HOST', '0.0.0.0')
    app.run(host=host, port=port, debug=app.config['DEBUG'])