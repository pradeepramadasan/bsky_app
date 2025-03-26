# Change to absolute imports
from agents import initialize_agents  # Remove the dot
from workflow import (
    process_post_workflow, show_post_plan,
    process_reply_workflow, show_reply_plan,
    search_subject_flow, show_search_plan
)

def main():
    """Main function to drive the Bluesky posting, replying, and subject search workflows."""
    # Initialize agents
    agents = initialize_agents()
    
    # Main menu loop
    while True:
        print("\nChoose an action:")
        print("1. Post a message to Bluesky")
        print("2. Process replies to Bluesky messages")
        print("3. Search messages by subject and possibly reply")
        print("4. Exit")
        
        choice = agents["sanjay"].get_human_input("Enter your choice (1, 2, 3, or 4): ").strip()
        
        if choice == "1":
            show_post_plan()
            user_input = agents["sanjay"].get_human_input("Enter the message to post: ").strip()
            if user_input:
                process_post_workflow(user_input, agents)
            else:
                print("No message entered.")
                
        elif choice == "2":
            show_reply_plan()
            process_reply_workflow(agents)
            
        elif choice == "3":
            show_search_plan()
            search_subject_flow(agents)
            
        elif choice == "4":
            print("Exiting the script.")
            break
            
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")

if __name__ == "__main__":
    main()