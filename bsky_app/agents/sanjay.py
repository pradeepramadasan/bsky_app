# filepath: atproto_app/agents/sanjay.py
from autogen import UserProxyAgent

def create_sanjay_agent():
    """Create and return the Sanjay (User Interface) agent"""
    return UserProxyAgent(
        name="Sanjay",
        human_input_mode="ALWAYS",
        system_message=(
            "You are Sanjay, responsible for interacting with the human user. "
            "Present numbered lists of messages clearly (1 to 20), and allow users to enter free-text instructions in English. "
            "Always structure your responses in JSON format with 'input_type', 'content', 'analysis', and 'user_feedback'."
        ),
        code_execution_config=False
    )