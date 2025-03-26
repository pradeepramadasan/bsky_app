from autogen import AssistantAgent
from config import config_list_gpt4o  # Changed from ..config
from utils.bluesky import post_to_bluesky_wrapper, fetch_bluesky_following_wrapper  # This is fine


def create_bheeman_agent():
    """Create and return the Bheeman (Posting) agent"""
    bheeman_tools = {
        "post_to_bluesky": post_to_bluesky_wrapper,
        "fetch_bluesky_following": fetch_bluesky_following_wrapper
    }
    
    return AssistantAgent(
        name="Bheeman",
        system_message=(
            "You are Bheeman, the posting agent. Your role is to post messages to Bluesky. "
            "Always return your output in JSON format with 'status', 'formatted_message', and 'result'."
        ),
        llm_config={"config_list": config_list_gpt4o, "functions": [
            bheeman_tools["post_to_bluesky"],
            bheeman_tools["fetch_bluesky_following"]
        ]},
        function_map={
            "post_to_bluesky": post_to_bluesky_wrapper,
            "fetch_bluesky_following": fetch_bluesky_following_wrapper
        }
    )