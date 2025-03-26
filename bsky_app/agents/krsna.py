from autogen import AssistantAgent
from config import config_list_gpt4o  # Changed from relative to absolute import

def create_krsna_agent():
    """Create and return the Krsna (Strategist) agent"""
    return AssistantAgent(
        name="Krsna",
        system_message=(
            "You are Krsna, the strategist and thinker. Analyze a message's intent and tone, and rewrite it concisely. "
            "Rewrite the provided message in 180 characters with a left-leaning tone. "
            "Return your response in JSON format with the key 'formatted_message'."
        ),
        llm_config={"config_list": config_list_gpt4o}
    )