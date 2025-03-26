# filepath: atproto_app/agents/yudhistran.py
from autogen import AssistantAgent
from config import config_list_gpt4o
from utils.bluesky import reply_to_bluesky_wrapper

def create_yudhistran_agent():
    """Create and return the Yudhistran (Mediator) agent"""
    return AssistantAgent(
        name="Yudhistran",
        system_message=(
            "You are Yudhistran, the mediator. Respond with a balanced and soothing tone to messages categorized as 'far-left'. "
            "Return your response in JSON format with 'status', 'formatted_message', and 'result'."
        ),
        llm_config={"config_list": config_list_gpt4o, "functions": [
            {"name": "reply_to_bluesky", "parameters": {}}
        ]},
        function_map={"reply_to_bluesky": reply_to_bluesky_wrapper}
    )