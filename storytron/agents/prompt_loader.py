import os
import warnings

def load_prompt(agent_id, satisfied=False):
    """Load system prompt for an agent from file."""
    if satisfied:
        prompt_file = os.path.join(os.path.dirname(__file__), '..', 'prompts', f'{agent_id}_satisfied.txt')
        # Fallback to regular prompt if satisfied prompt doesn't exist
        if not os.path.exists(prompt_file):
            warnings.warn(f"Satisfied prompt file not found for agent '{agent_id}'. Falling back to regular prompt.")
            prompt_file = os.path.join(os.path.dirname(__file__), '..', 'prompts', f'{agent_id}.txt')
    else:
        prompt_file = os.path.join(os.path.dirname(__file__), '..', 'prompts', f'{agent_id}.txt')

    try:
        with open(prompt_file, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        return f"Error: Prompt file not found for agent {agent_id}"

def save_prompt(agent_id, content):
    """Save system prompt for an agent to file."""
    prompt_file = os.path.join(os.path.dirname(__file__), '..', 'prompts', f'{agent_id}.txt')
    os.makedirs(os.path.dirname(prompt_file), exist_ok=True)
    with open(prompt_file, 'w', encoding='utf-8') as f:
        f.write(content)

def list_available_prompts():
    """List all available prompt files."""
    prompts_dir = os.path.join(os.path.dirname(__file__), '..', 'prompts')
    if not os.path.exists(prompts_dir):
        return []

    prompts = []
    satisfied_prompts = []
    for filename in os.listdir(prompts_dir):
        if filename.endswith('.txt'):
            if filename.endswith('_satisfied.txt'):
                agent_id = filename[:-13]  # Remove _satisfied.txt extension
                satisfied_prompts.append(agent_id)
            else:
                agent_id = filename[:-4]  # Remove .txt extension
                prompts.append(agent_id)

    return sorted(prompts), sorted(satisfied_prompts)

def has_satisfied_prompt(agent_id):
    """Check if an agent has a satisfied prompt file."""
    prompt_file = os.path.join(os.path.dirname(__file__), '..', 'prompts', f'{agent_id}_satisfied.txt')
    return os.path.exists(prompt_file)
