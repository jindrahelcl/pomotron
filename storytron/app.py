from flask import Flask, request, jsonify, render_template, redirect, url_for
from werkzeug.middleware.proxy_fix import ProxyFix
import os
import jsonlines
from datetime import datetime
from dotenv import load_dotenv
from agents.joystick import JoystickAgent
from agents.confessor import ConfessorAgent
from agents.openai import OpenAIAgent
from agents.prompt_loader import load_prompt, save_prompt, list_available_prompts
from story import Story
import json


# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

# Configuration from environment variables
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['APPLICATION_ROOT'] = '/'
app.config['HOST'] = os.environ.get('HOST', '0.0.0.0')
app.config['PORT'] = int(os.environ.get('PORT', 5000))
app.config['OPENAI_API_KEY'] = os.environ.get('OPENAI_API_KEY')

HISTORY_FILE = os.environ.get('HISTORY_FILE', 'message_history.jsonl')

@app.before_request
def log_request():
    if request.path.startswith('/api/chat'):
        message = ""
        if request.is_json:
            try:
                data = request.get_json()
                message = data.get('message', '').replace('\n', ' ')[:100]
            except:
                message = "[JSON parse error]"
        print(f"{datetime.now()} - {request.method} {request.path} - message: {message}")

@app.after_request
def log_response(response):
    if request.path.startswith('/api/chat'):
        agent_response = ""
        try:
            response_data = json.loads(response.get_data(as_text=True))
            agent_response = response_data.get('agent_response', '').replace('\n', ' ')[:100]
        except:
            agent_response = "[Response parse error]"
        print(f"{datetime.now()} - {response.status_code} {request.path} - agent_response: {agent_response}")
    return response

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

def get_story():
    """Get a fresh story instance with loaded state for each request."""
    story = Story([
        OpenAIAgent("start", "Start Agent"),
        OpenAIAgent("shot_out_eye", "ShotOutEye Agent"),
        JoystickAgent(),
        OpenAIAgent("aida", "Aida Agent"),
        OpenAIAgent("dry_gum", "DryGum Agent"),
        OpenAIAgent("washer_woman", "WasherWoman Agent"),
        OpenAIAgent("tradicni", "Tradicni Agent"),
        OpenAIAgent("final_boss", "Final Boss Agent"),
        OpenAIAgent("final_boss_2", "Final Boss Stage 2"),
        OpenAIAgent("final_boss_3", "Final Boss Stage 3"),
        OpenAIAgent("nahodny_kolemjdouci", "Náhodný Kolemjdoucí"),
        ConfessorAgent()
    ])

    # Initialize state file from default if it doesn't exist
    if not os.path.exists('story_state.json'):
        if os.path.exists('default_story_state.json'):
            import shutil
            shutil.copy('default_story_state.json', 'story_state.json')

    story.load_state()
    return story

@app.route('/')
def pomo_interface():
    return render_template('pomo.html')

@app.route('/api/keepalive', methods=['POST'])
def keep_alive():
    # TODO: Log the keep-alive, update last-seen timestamp, etc.
    return '', 200

@app.route('/web')
def dashboard():
    story = get_story()
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
    story = get_story()
    available_agents = story.to_listing()
    return render_template('agents.html',
                         agents={'agents': available_agents, 'active_agent': story.current_id})

@app.route('/web/history')
def web_history():
    return render_template('history.html')

@app.route('/web/prompts')
def web_prompts():
    regular_prompts, satisfied_prompts = list_available_prompts()
    prompts_data = []

    # Add regular prompts
    for agent_id in regular_prompts:
        try:
            content = load_prompt(agent_id)
            prompts_data.append({
                'agent_id': agent_id,
                'content': content,
                'preview': content[:200] + '...' if len(content) > 200 else content,
                'type': 'regular'
            })
        except Exception as e:
            prompts_data.append({
                'agent_id': agent_id,
                'content': f"Error loading prompt: {str(e)}",
                'preview': f"Error: {str(e)}",
                'type': 'regular'
            })

    # Add satisfied prompts
    for agent_id in satisfied_prompts:
        try:
            content = load_prompt(agent_id, satisfied=True)
            prompts_data.append({
                'agent_id': f"{agent_id}_satisfied",
                'content': content,
                'preview': content[:200] + '...' if len(content) > 200 else content,
                'type': 'satisfied'
            })
        except Exception as e:
            prompts_data.append({
                'agent_id': f"{agent_id}_satisfied",
                'content': f"Error loading prompt: {str(e)}",
                'preview': f"Error: {str(e)}",
                'type': 'satisfied'
            })

    return render_template('prompts.html', prompts=prompts_data)

@app.route('/switch-agent', methods=['POST'])
def web_switch_agent():
    story = get_story()
    agent_id = request.form.get('agent_id')
    if agent_id and agent_id in story.agents:
        story.set_active(agent_id)
        return redirect(url_for('web_agents'))
    return redirect(url_for('web_agents'))

@app.route('/toggle-agent-satisfaction', methods=['POST'])
def toggle_agent_satisfaction():
    story = get_story()
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
    story = get_story()
    story.reset_story()
    return redirect(url_for('web_agents'))

@app.route('/api/agents', methods=['GET'])
def list_agents():
    story = get_story()
    available_agents = story.to_listing()
    return jsonify({
        'agents': available_agents,
        'active_agent': story.current_id
    })

@app.route('/api/agents/<agent_id>/activate', methods=['POST'])
def switch_agent(agent_id):
    story = get_story()
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
    story = get_story()
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
    story = get_story()
    data = request.get_json()

    if not data or 'message' not in data:
        return jsonify({
            'error': 'Message is required'
        }), 400

    message = data.get('message', '')
    sender = data.get('sender', 'web')  # 'web' or 'pomo'

    agent_response = story.chat(message)
    timestamp = datetime.now().isoformat()

    # Save story state after chat (important for satisfaction state changes)
    story._save_state()

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
        'timestamp': timestamp,
        'tts_engine': story.active_agent.tts_engine,
        'tts_voice': story.active_agent.tts_voice,
        'victory': story.active_agent.is_satisfied() and story.current_id == "tradicni"
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

@app.route('/api/history/<timestamp>', methods=['DELETE'])
def delete_history_message(timestamp):
    """Delete a specific message from history by timestamp."""
    try:
        current_history = load_history()
        # Filter out the message with the specified timestamp
        filtered_history = [msg for msg in current_history if msg.get('timestamp') != timestamp]

        if len(filtered_history) == len(current_history):
            return jsonify({'error': 'Message not found'}), 404

        # Save the filtered history back
        save_history(filtered_history)

        return jsonify({
            'message': 'Message deleted successfully',
            'deleted_timestamp': timestamp,
            'remaining_count': len(filtered_history)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/agents/<agent_id>/memory', methods=['GET'])
def get_agent_memory(agent_id):
    story = get_story()
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
    story = get_story()
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

@app.route('/api/agents/<agent_id>/history', methods=['DELETE'])
def clear_agent_history(agent_id):
    story = get_story()
    if agent_id not in story.agents:
        return jsonify({'error': f'Agent {agent_id} not found'}), 404

    # Get the agent and clear its memory/quest state
    agent = story.agents[agent_id]
    if agent.enable_memory:
        agent.clear_memory()  # This will also reset quest state for joystick agent

    # Load current history
    current_history = load_history()

    # Filter out messages from this specific agent
    filtered_history = [entry for entry in current_history if entry.get('agent') != agent_id]

    # Save the filtered history back
    save_history(filtered_history)

    removed_count = len(current_history) - len(filtered_history)

    return jsonify({
        'message': f'History cleared for agent {agent_id}',
        'agent_id': agent_id,
        'removed_count': removed_count,
        'remaining_count': len(filtered_history)
    })

@app.route('/api/agents/<agent_id>/history', methods=['GET'])
def get_agent_history_count(agent_id):
    story = get_story()
    if agent_id not in story.agents:
        return jsonify({'error': f'Agent {agent_id} not found'}), 404

    # Load current history and count messages for this agent
    current_history = load_history()
    agent_history_count = sum(1 for entry in current_history if entry.get('agent') == agent_id)

    return jsonify({
        'agent_id': agent_id,
        'history_count': agent_history_count,
        'total_history_count': len(current_history)
    })

@app.route('/api/prompts', methods=['GET'])
def list_prompts():
    """List all available prompts."""
    regular_prompts, satisfied_prompts = list_available_prompts()
    prompts_data = []

    # Add regular prompts
    for agent_id in regular_prompts:
        try:
            content = load_prompt(agent_id)
            prompts_data.append({
                'agent_id': agent_id,
                'type': 'regular',
                'content': content,
                'preview': content[:200] + '...' if len(content) > 200 else content,
                'length': len(content)
            })
        except Exception as e:
            prompts_data.append({
                'agent_id': agent_id,
                'type': 'regular',
                'error': str(e),
                'preview': f"Error: {str(e)}"
            })

    # Add satisfied prompts
    for agent_id in satisfied_prompts:
        try:
            content = load_prompt(agent_id, satisfied=True)
            prompts_data.append({
                'agent_id': agent_id,
                'type': 'satisfied',
                'content': content,
                'preview': content[:200] + '...' if len(content) > 200 else content,
                'length': len(content)
            })
        except Exception as e:
            prompts_data.append({
                'agent_id': agent_id,
                'type': 'satisfied',
                'error': str(e),
                'preview': f"Error: {str(e)}"
            })

    return jsonify({
        'prompts': prompts_data,
        'count': len(prompts_data)
    })

@app.route('/api/prompts/<agent_id>', methods=['GET'])
def get_prompt(agent_id):
    """Get prompt content for a specific agent."""
    try:
        # Check if this is a satisfied prompt
        if agent_id.endswith('_satisfied'):
            base_agent_id = agent_id[:-10]  # Remove '_satisfied'
            content = load_prompt(base_agent_id, satisfied=True)
        else:
            content = load_prompt(agent_id)

        return jsonify({
            'agent_id': agent_id,
            'content': content,
            'length': len(content)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/api/prompts/<agent_id>', methods=['PUT'])
def update_prompt(agent_id):
    """Update prompt content for a specific agent."""
    data = request.get_json()

    if not data or 'content' not in data:
        return jsonify({'error': 'Content is required'}), 400

    content = data['content']

    try:
        # Check if this is a satisfied prompt
        if agent_id.endswith('_satisfied'):
            base_agent_id = agent_id[:-10]  # Remove '_satisfied'
            save_prompt(base_agent_id, content, satisfied=True)
        else:
            save_prompt(agent_id, content, satisfied=False)

        return jsonify({
            'message': f'Prompt updated for agent {agent_id}',
            'agent_id': agent_id,
            'content': content,
            'length': len(content)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/agents/<agent_id>/tts', methods=['GET'])
def get_agent_tts_config(agent_id):
    """Get TTS configuration for a specific agent."""
    story = get_story()
    if agent_id not in story.agents:
        return jsonify({'error': f'Agent {agent_id} not found'}), 404

    agent = story.agents[agent_id]
    return jsonify({
        'agent_id': agent_id,
        'tts_engine': agent.tts_engine,
        'tts_voice': agent.tts_voice,
        'supported_voices': agent.get_supported_voices()
    })

@app.route('/api/agents/<agent_id>/tts', methods=['PUT'])
def update_agent_tts_config(agent_id):
    """Update TTS configuration for a specific agent."""
    story = get_story()
    if agent_id not in story.agents:
        return jsonify({'error': f'Agent {agent_id} not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body is required'}), 400

    agent = story.agents[agent_id]

    try:
        engine = data.get('tts_engine', agent.tts_engine)
        voice = data.get('tts_voice', agent.tts_voice)

        agent.set_tts_config(engine, voice)
        story._save_state()

        return jsonify({
            'message': f'TTS configuration updated for agent {agent_id}',
            'agent_id': agent_id,
            'tts_engine': agent.tts_engine,
            'tts_voice': agent.tts_voice
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/tts/engines', methods=['GET'])
def get_tts_engines():
    """Get available TTS engines and their supported voices."""
    from agents.base import BaseAgent
    return jsonify({
        'engines': BaseAgent.TTS_ENGINES
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
    app.run(host=app.config['HOST'], port=app.config['PORT'], debug=False)
