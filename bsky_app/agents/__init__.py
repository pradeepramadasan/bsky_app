# Change to local relative imports - note the period before each module name
from .sanjay import create_sanjay_agent
from .krsna import create_krsna_agent
from .bheeman import create_bheeman_agent
from .arjunan import create_arjunan_agent
from .yudhistran import create_yudhistran_agent
from .nakulan import create_nakulan_agent
from autogen import GroupChat, GroupChatManager
from config import config_list_gpt4o  # This is correct (absolute import)

def initialize_agents():
    """Initialize all agents and return them as a dictionary"""
    sanjay = create_sanjay_agent()
    krsna = create_krsna_agent()
    bheeman = create_bheeman_agent()
    arjunan = create_arjunan_agent()
    yudhistran = create_yudhistran_agent()
    nakulan = create_nakulan_agent()
    
    return {
        "sanjay": sanjay,
        "krsna": krsna,
        "bheeman": bheeman,
        "arjunan": arjunan,
        "yudhistran": yudhistran,
        "nakulan": nakulan
    }

def setup_group_chat(agents_dict):
    """Set up the group chat for agent collaboration"""
    agents_list = list(agents_dict.values())
    group_chat = GroupChat(agents=agents_list, messages=[], max_round=20)
    manager = GroupChatManager(groupchat=group_chat, llm_config={"config_list": config_list_gpt4o})
    
    return group_chat, manager