from flask import Flask, request, jsonify, render_template, redirect, url_for
from werkzeug.middleware.proxy_fix import ProxyFix
import os
import jsonlines
from datetime import datetime
from agents import DefaultAgent, NegativeAgent, StartAgent, DryGumAgent, JoystickAgent, ShotOutEyeAgent, AidaAgent, WasherWomanAgent, TradicniAgent, ConfessorAgent
from story import Story

app = Flask(__name__)
app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

app.config['DEBUG'] = os.environ.get('DEBUG', 'False').lower() == 'true'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['APPLICATION_ROOT'] = '/'

HISTORY_FILE = os.environ.get('HISTORY_FILE', 'message_history.jsonl')

def load_history():
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with jsonlines.open(HISTORY_FILE) as reader:
                for entry in reader:
                    history.append(entry)
        except Exception as e:
            print(f"Error loading history: {e}")
    return history

def save_history(history):
    try:
        with jsonlines.open(HISTORY_FILE, mode='w') as writer:
            for entry in history:
                writer.write(entry)
    except Exception as e:
        print(f"Error saving history: {e}")

def append_to_history(entry):
    try:
        with jsonlines.open(HISTORY_FILE, mode='a') as writer:
            writer.write(entry)
    except Exception as e:
        print(f"Error appending to history: {e}")

def get_current_history():
    return load_history()

story = Story([
    DefaultAgent(),
    NegativeAgent(),
    StartAgent(),
    ShotOutEyeAgent(),
    JoystickAgent(),
    AidaAgent(),
    DryGumAgent(),
    WasherWomanAgent(),
    TradicniAgent(),
    ConfessorAgent()
])

# Initialize state file from default if it doesn't exist
if not os.path.exists('story_state.json'):
    if os.path.exists('default_story_state.json'):
        import shutil
        shutil.copy('default_story_state.json', 'story_state.json')

story.load_state()

@app.route('/')
def pomo_interface():
    return render_template('pomo.html')

@app.route('/api/keepalive', methods=['POST'])
def keep_alive():
    # TODO: Log the keep-alive, update last-seen timestamp, etc.
    return '', 200

@app.route('/web')
def dashboard():
    available_agents = story.to_listing()
    status = {
        'status': 'alive',
        'service': 'StoryTRON',
        'active_agent': story.current_id
    }

    return render_template('dashboard.html',
                        status=status,
                        agents={'agents': available_agents, 'active_agent': story.current_id},
                        timestamp=datetime.now().strftime('%H:%M:%S'))

@app.route('/web/agents')
def web_agents():
    available_agents = story.to_listing()
    return render_template('agents.html',
                         agents={'agents': available_agents, 'active_agent': story.current_id})

@app.route('/web/history')
def web_history():
    return render_template('history.html')

@app.route('/switch-agent', methods=['POST'])
def web_switch_agent():
    agent_id = request.form.get('agent_id')
    if agent_id and agent_id in story.agents:
        story.set_active(agent_id)
        return redirect(url_for('web_agents'))
    return redirect(url_for('web_agents'))

@app.route('/toggle-agent-satisfaction', methods=['POST'])
def toggle_agent_satisfaction():
    agent_id = request.form.get('agent_id')
    if agent_id and agent_id in story.agents:
        agent = story.agents[agent_id]
        if agent.is_satisfied():
            agent.reset_satisfaction()
        else:
            agent.mark_satisfied()
        story._save_state()
    return redirect(url_for('web_agents'))

@app.route('/reset-story', methods=['POST'])
def reset_story():
    story.reset_story()
    return redirect(url_for('web_agents'))

@app.route('/api/agents', methods=['GET'])
def list_agents():
    available_agents = story.to_listing()
    return jsonify({
        'agents': available_agents,
        'active_agent': story.current_id
    })

@app.route('/api/agents/<agent_id>/activate', methods=['POST'])
def switch_agent(agent_id):
    if agent_id in story.agents:
        story.set_active(agent_id)
        return jsonify({
            'message': f'Switched to agent: {agent_id}',
            'active_agent': story.current_id
        })
    else:
        return jsonify({
            'error': f'Agent {agent_id} not found'
        }), 404

@app.route('/api/agents/<agent_id>/satisfaction', methods=['POST'])
def toggle_agent_satisfaction_api(agent_id):
    if agent_id not in story.agents:
        return jsonify({'error': f'Agent {agent_id} not found'}), 404

    agent = story.agents[agent_id]
    if agent.is_satisfied():
        agent.reset_satisfaction()
    else:
        agent.mark_satisfied()
    story._save_state()

    return jsonify({
        'message': f'Agent {agent_id} satisfaction toggled',
        'agent_id': agent_id,
        'satisfied': agent.is_satisfied()
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()

    if not data or 'message' not in data:
        return jsonify({
            'error': 'Message is required'
        }), 400

    message = data.get('message', '')
    sender = data.get('sender', 'web')  # 'web' or 'pomo'

    agent_response = story.chat(message)
    timestamp = datetime.now().isoformat()

    entry = {
        'timestamp': timestamp,
        'sender': sender,
        'message': message,
        'response': agent_response,
    'agent': story.current_id
    }

    append_to_history(entry)

    return jsonify({
    'active_agent': story.current_id,
        'user_message': message,
        'agent_response': agent_response,
        'timestamp': timestamp
    })

@app.route('/api/history', methods=['GET'])
def get_history():
    current_history = get_current_history()
    return jsonify({
        'history': current_history,
        'count': len(current_history)
    })

@app.route('/api/history', methods=['DELETE'])
def clear_history():
    # Remove history file
    if os.path.exists(HISTORY_FILE):
        try:
            os.remove(HISTORY_FILE)
        except Exception as e:
            print(f"Error removing history file: {e}")

    return jsonify({'message': 'History cleared'})

@app.route('/api/agents/<agent_id>/memory', methods=['GET'])
def get_agent_memory(agent_id):
    if agent_id not in story.agents:
        return jsonify({'error': f'Agent {agent_id} not found'}), 404
    
    agent = story.agents[agent_id]
    memory_summary = agent.get_memory_summary()
    
    return jsonify({
        'agent_id': agent_id,
        'memory_enabled': agent.enable_memory,
        'memory_count': len(agent.conversation_memory) if agent.conversation_memory else 0,
        'memory_size': agent.memory_size if agent.enable_memory else 0,
        'recent_summary': memory_summary
    })

@app.route('/api/agents/<agent_id>/memory', methods=['DELETE'])
def clear_agent_memory(agent_id):
    if agent_id not in story.agents:
        return jsonify({'error': f'Agent {agent_id} not found'}), 404
    
    agent = story.agents[agent_id]
    if not agent.enable_memory:
        return jsonify({'error': f'Agent {agent_id} does not have memory enabled'}), 400
    
    agent.clear_memory()
    story._save_state()  # Save the cleared memory state
    
    return jsonify({
        'message': f'Memory cleared for agent {agent_id}',
        'agent_id': agent_id
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
