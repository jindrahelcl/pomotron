import os

def load_prompt(agent_id):
    """Load system prompt for an agent from file."""
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
    for filename in os.listdir(prompts_dir):
        if filename.endswith('.txt'):
            agent_id = filename[:-4]  # Remove .txt extension
            prompts.append(agent_id)

    return sorted(prompts)
