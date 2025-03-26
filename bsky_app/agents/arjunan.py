from autogen import AssistantAgent
from config import config_list_gpt4o  # Changed from ..config
from utils.bluesky import reply_to_bluesky_wrapper  # This is fine


def create_arjunan_agent():
    """Create and return the Arjunan (Responder) agent"""
    return AssistantAgent(
        name="Arjunan",
        system_message=(
            "You are Arjunan, the reactive responder. Post reply messages with a left-leaning perspective. "
            "Ensure your tone is assertive and progressive, and respond in JSON format."
        ),
        llm_config={"config_list": config_list_gpt4o, "functions": [ 
            {"name": "reply_to_bluesky", "parameters": {}}
        ]},
        function_map={"reply_to_bluesky": reply_to_bluesky_wrapper}
    )