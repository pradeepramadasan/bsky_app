# filepath: atproto_app/agents/nakulan.py
from autogen import AssistantAgent
from config import config_list_gpt4o

def create_nakulan_agent():
    """Create and return the Nakulan (Search) agent"""
    return AssistantAgent(
        name="Nakulan",
        system_message=(
            "You are Nakulan, the search agent. Extract DID information from a list of messages. "
            "Return a JSON array where each element includes 'message' and 'did' fields."
        ),
        llm_config={"config_list": config_list_gpt4o}
    )