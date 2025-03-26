# filepath: atproto_app/workflow/post_workflow.py
import json
from utils.helpers import extract_json_content
from utils.bluesky import post_to_bluesky_wrapper

def show_post_plan():
    """Display the plan for posting a message"""
    print("\nPlan for Posting a Message:")
    print("Steps:")
    print("  1. Sanjay collects your message.")
    print("  2. Krsna rewrites the message in 180 characters using a bold left-leaning tone that challenges oligarch power.")
    print("  3. Sanjay presents both the original and rewritten message for your feedback.")
    print("  4. Based on your input, the preferred message is posted by Bheeman.")
    print("Agents Involved:")
    print("  - Sanjay (User Interaction)")
    print("  - Krsna (Strategist/Rewriter)")
    print("  - Bheeman (Poster)\n")

def process_post_workflow(user_input, agents):
    """
    Orchestrate posting a message using the collaborative agent workflow.
    
    Args:
        user_input (str): The original message from the user
        agents (dict): Dictionary of initialized agents
    """
    # Extract agents
    sanjay = agents["sanjay"]
    krsna = agents["krsna"]
    
    # Step 1: Collect the original message.
    original_message = user_input

    # Step 2: Ask Krsna to rewrite the message.
    rewrite_prompt = json.dumps({
        "original_message": original_message,
        "instruction": (
            "You are Krsna, the strategist. Rewrite the above message within 180 characters "
            "using a bold left-leaning tone that emphasizes social justice and challenges the oligarchs. "
            "Return your answer in a JSON object with the key 'formatted_message'."
        )
    })
    krsna_response = krsna.generate_reply(messages=[{"role": "user", "content": rewrite_prompt}])
    if isinstance(krsna_response, str):
        krsna_content = krsna_response
    elif isinstance(krsna_response, dict):
        krsna_content = krsna_response.get("content", "")
    else:
        krsna_content = getattr(krsna_response, "content", "")
    krsna_content = extract_json_content(krsna_content)
    try:
        krsna_json = json.loads(krsna_content)
        rewritten_message = krsna_json.get("formatted_message", "")
    except json.JSONDecodeError:
        rewritten_message = krsna_content  # Fallback if JSON parsing fails

    if not rewritten_message:
        rewritten_message = original_message  # Fallback if no rewrite obtained

    # Step 3: Present both messages for user feedback.
    summary = (
        "Original Message:\n" + original_message + "\n\n" +
        "Rewritten (Left-Leaning, 180-char) Message:\n" + rewritten_message + "\n\n" +
        "Which message would you like to post? Type 'revised' to post the rewritten message, or 'original' to post your original message."
    )
    user_choice = sanjay.get_human_input(summary).strip().lower()

    # Step 4: Interpret user feedback.
    if user_choice == "revised":
        final_message = rewritten_message
    elif user_choice == "original":
        final_message = original_message
    else:
        clarification = sanjay.get_human_input("Invalid choice. Please type 'revised' or 'original': ").strip().lower()
        final_message = rewritten_message if clarification == "revised" else original_message

    # Step 5: Post the final message.
    post_result_json = post_to_bluesky_wrapper(final_message)
    post_result = json.loads(post_result_json)
    if post_result.get("status") == "success":
        print("Message posted successfully.")
    else:
        print("Error posting message:", post_result.get("message"))