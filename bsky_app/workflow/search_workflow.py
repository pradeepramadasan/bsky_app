# filepath: atproto_app/workflow/search_workflow.py
import json
from utils.helpers import extract_json_content, trim_text
from utils.bluesky import like_bluesky_wrapper, reply_to_bluesky_wrapper, bluesky_login
import os

def show_search_plan():
    """Display the plan for search workflow"""
    print("\nPlan for Subject Search:")
    print("Steps:")
    print("  1. You provide a subject keyword")
    print("  2. Nakulan searches the latest 20 messages for that subject")
    print("  3. Sanjay displays the matching messages")
    print("  4. You select a message to reply to")
    print("  5. You choose between writing your own reply or using an agent-generated one")
    print("  6. For agent replies, Krsna categorizes the message")
    print("  7. Either Arjunan or Yudhistran generates a reply based on the categorization")
    print("  8. Krsna rewrites the reply to 180 characters")
    print("  9. You confirm, and Bheeman posts the reply")
    print("Agents Involved:")
    print("  - Sanjay (User Interaction)")
    print("  - Nakulan (Search Specialist)")
    print("  - Krsna (Categorizer/Editor)")
    print("  - Arjunan / Yudhistran (Responders)")
    print("  - Bheeman (Poster)")

def search_subject_flow(agents):
    """
    This flow allows searching for messages from a specific user on Bluesky,
    analyzing them, and responding using the collaborative agent workflow.
    
    Args:
        agents (dict): Dictionary of initialized agents
    """
    # Extract agents
    sanjay = agents["sanjay"]
    krsna = agents["krsna"]
    arjunan = agents["arjunan"]
    yudhistran = agents["yudhistran"]
    nakulan = agents["nakulan"]
    
    # Step 1: Sanjay collects the username to search for
    username = sanjay.get_human_input("Enter the username to search (without '@'): ").strip()
    if not username:
        print("No username entered. Aborting search.")
        return

    # Step 2: Search for the user and fetch messages
    client = bluesky_login()
    
    print(f"Searching for user '{username}'...")
    
    # Search for the user
    try:
        # Search for user
        search_results = client.app.bsky.actor.search_actors({"term": username})
        
        # Find the exact match for the username or similar results
        user_did = None
        for result in search_results.actors:
            if username.lower() in result.handle.lower():  # Perform a partial match
                user_did = result.did  # Return the user's decentralized identifier (DID)
                print(f"Found user: {result.display_name} (@{result.handle})")
                break
                
        if not user_did:
            print(f"User '{username}' not found.")
            return
            
        # Retrieve latest 20 messages from the user
        print(f"Fetching latest messages from @{username}...")
        try:
            feed = client.app.bsky.feed.get_author_feed({"actor": user_did, "limit": 20})
            messages = []
            
            for idx, feed_view in enumerate(feed.feed, start=1):
                post = feed_view.post
                messages.append({
                    "number": idx,
                    "did": post.uri,
                    "author": post.author.display_name or post.author.handle,
                    "text": post.record.text,
                    "timestamp": post.indexed_at
                })
                
            if not messages:
                print(f"No messages found from @{username}.")
                return
                
        except Exception as e:
            print(f"Error retrieving messages: {e}")
            return
            
    except Exception as e:
        print(f"Error during user search: {e}")
        return

    # Step 3: Ask Krsna to analyze these messages for intent and tone
    print("Analyzing messages...")
    analyze_prompt = json.dumps({
        "task": "analyze_messages",
        "messages": messages,
        "instruction": (
            "You are Krsna, the strategist. Analyze each message to determine:"
            "1. Subject matter (main topic)"
            "2. Communication style (formal, casual, aggressive, etc.)"
            "3. Category (neutral, informational, opinion, question)"
            "For each message, provide 'message_id', 'subject', 'style', and 'category'."
        )
    })
    
    krsna_analysis = krsna.generate_reply(messages=[{"role": "user", "content": analyze_prompt}])
    if isinstance(krsna_analysis, str):
        analysis_content = krsna_analysis
    elif isinstance(krsna_analysis, dict):
        analysis_content = krsna_analysis.get("content", "")
    else:
        analysis_content = getattr(krsna_analysis, "content", "")
    analysis_content = extract_json_content(analysis_content)
    
    # Parse the analysis
    try:
        analysis_results = json.loads(analysis_content)
        if isinstance(analysis_results, list):
            analyzed_messages = analysis_results
        else:
            # Try to extract a list from the JSON
            for key in analysis_results:
                if isinstance(analysis_results[key], list):
                    analyzed_messages = analysis_results[key]
                    break
            else:
                print("Analysis format unexpected. Using default analysis.")
                analyzed_messages = []
    except:
        print("Analysis parsing failed. Using default analysis.")
        analyzed_messages = []
    
    # Merge analysis with messages
    for msg in messages:
        msg_number = msg.get("number")
        analysis = next((a for a in analyzed_messages if a.get("message_id") == msg_number), None)
        if analysis:
            msg["subject"] = analysis.get("subject", "Unknown")
            msg["style"] = analysis.get("style", "Unknown")
            msg["category"] = analysis.get("category", "Unknown")
            msg["analysis"] = f"Subject: {msg['subject']}, Style: {msg['style']}, Category: {msg['category']}"
        else:
            msg["subject"] = "Unknown"
            msg["style"] = "Unknown"
            msg["category"] = "Unknown"
            msg["analysis"] = "Not analyzed"

    # Step 4: Sanjay displays the numbered list of messages with analysis
    print(f"\nLatest messages from @{username}:")
    for msg in messages:
        number = msg.get("number", "?")
        text = msg.get("text", "(No text)")[:80]  # Trim for display
        analysis = msg.get("analysis", "Not analyzed")
        print(f"{number}. {text}\n   Analysis: {analysis}")

    # Step 5: User selects a message to interact with
    selection = sanjay.get_human_input("\nEnter message number to interact with (or 'skip'): ").strip().lower()
    if selection == "skip":
        print("Interaction cancelled.")
        return
        
    try:
        selected_number = int(selection)
        selected_message = next((m for m in messages if m.get("number") == selected_number), None)
        if not selected_message:
            print("No message found with that number.")
            return
    except ValueError:
        print("Invalid number entered.")
        return
    
    # Step 6: Ask if user wants to like the message
    like_option = sanjay.get_human_input("Would you like to like this message? (yes/no): ").strip().lower()
    if like_option == "yes":
        like_result_json = like_bluesky_wrapper(post_uri=selected_message["did"])
        like_result = json.loads(like_result_json)
        if like_result["status"] == "success":
            print("Message liked successfully.")
        else:
            print("Error liking message:", like_result["message"])
    
    # Step 7: Ask if user wants to reply to the message
    reply_option = sanjay.get_human_input("Would you like to reply to this message? (yes/no): ").strip().lower()
    if reply_option != "yes":
        print("No reply will be created. Workflow completed.")
        return
    
    # Step 8: Get reply type (human or agent)
    reply_type = sanjay.get_human_input("Type 'human' for your own reply or 'agent' for agent-generated reply: ").strip().lower()
    
    if reply_type == "human":
        # Human-generated reply
        reply_text = sanjay.get_human_input("Enter your reply text: ")
    elif reply_type == "agent":
        # Step 9: Send to Krsna for political categorization
        print("Analyzing message political leaning...")
        categorize_prompt = json.dumps({
            "task": "categorize",
            "message": selected_message["text"],
            "instruction": (
                "Analyze this message and determine if it has a 'far-right' political leaning. "
                "Return a JSON object with: 'category' (either 'far-right' or 'other') and 'reasoning'."
            )
        })
        
        categorization = krsna.generate_reply(messages=[{"role": "user", "content": categorize_prompt}])
        cat_content = getattr(categorization, "content", categorization) if not isinstance(categorization, str) else categorization
        cat_content = extract_json_content(cat_content)
        
        # Parse categorization
        try:
            cat_json = json.loads(cat_content)
            category = cat_json.get("category", "other").lower()
            reasoning = cat_json.get("reasoning", "No reasoning provided")
            print(f"Message categorized as: {category}")
            print(f"Reasoning: {reasoning}")
        except:
            print("Categorization failed. Defaulting to 'other'.")
            category = "other"
        
        # Step 10: Select appropriate agent based on category
        if category == "far-right":
            print("Using Yudhistran (balanced mediator) for the reply...")
            agent_prompt = json.dumps({
                "task": "reply",
                "message": selected_message["text"],
                "instruction": (
                    "Create a balanced, mediating response to this far-right message. "
                    "Your response should be respectful while finding common ground. "
                    "Return a JSON object with key 'formatted_message' containing your response."
                )
            })
            reply_agent = yudhistran
        else:
            print("Using Arjunan (progressive responder) for the reply...")
            agent_prompt = json.dumps({
                "task": "reply",
                "message": selected_message["text"],
                "instruction": (
                    "Create a progressive response to this message. "
                    "Your response should emphasize social justice principles. "
                    "Return a JSON object with key 'formatted_message' containing your response."
                )
            })
            reply_agent = arjunan
        
        # Generate the reply
        agent_response = reply_agent.generate_reply(messages=[{"role": "user", "content": agent_prompt}])
        reply_content = getattr(agent_response, "content", agent_response) if not isinstance(agent_response, str) else agent_response
        reply_content = extract_json_content(reply_content)
        
        # Parse the reply
        try:
            reply_json = json.loads(reply_content)
            reply_text = reply_json.get("formatted_message", "")
            if not reply_text:
                for field in ["final_reply", "reply", "message", "text", "content"]:
                    if field in reply_json and reply_json.get(field, ""):
                        reply_text = reply_json.get(field, "")
                        break
        except:
            print("Failed to parse agent response. Using raw text.")
            reply_text = reply_content
        
        # Step 11: Send to Krsna for validation and editing to 180 characters
        validate_prompt = json.dumps({
            "task": "validate_and_edit",
            "reply_text": reply_text,
            "instruction": (
                "Validate this reply for appropriateness and edit it to exactly 180 characters. "
                "Return a JSON object with keys: 'edited_reply' and 'feedback'."
            )
        })
        
        krsna_validation = krsna.generate_reply(messages=[{"role": "user", "content": validate_prompt}])
        validation_content = getattr(krsna_validation, "content", krsna_validation) if not isinstance(krsna_validation, str) else krsna_validation
        validation_content = extract_json_content(validation_content)
        
        # Parse the validation
        try:
            validation_json = json.loads(validation_content)
            edited_reply = validation_json.get("edited_reply", reply_text)
            feedback = validation_json.get("feedback", "No feedback provided")
            print(f"Krsna's feedback: {feedback}")
            reply_text = edited_reply
        except:
            print("Validation parsing failed. Using original reply text.")
    else:
        print("Invalid reply type. Reply cancelled.")
        return
    
    # Step 12: Show user the final reply and get approval
    if len(reply_text) > 180:
        final_reply = reply_text[:177] + "..."  # Ensure it's 180 chars or less
    else:
        final_reply = reply_text
        
    print("\nFinal reply:")
    print(f"\"{final_reply}\"")
    
    approval = sanjay.get_human_input("Do you approve this reply? (yes/no): ").strip().lower()
    
    if approval != "yes":
        # Step 13: Feedback loop - ask for alternative or user's own reply
        alternative = sanjay.get_human_input("Type 'alternative' for another AI-generated reply, or type your own reply: ").strip()
        
        if alternative.lower() == "alternative":
            # Ask Krsna to create an alternative
            alt_prompt = json.dumps({
                "task": "alternative_reply",
                "original_message": selected_message["text"],
                "previous_reply": reply_text,
                "instruction": (
                    "Create an alternative reply that is significantly different from the previous one. "
                    "Ensure it's exactly 180 characters. Return a JSON with key 'formatted_message'."
                )
            })
            
            alt_response = krsna.generate_reply(messages=[{"role": "user", "content": alt_prompt}])
            alt_content = getattr(alt_response, "content", alt_response) if not isinstance(alt_response, str) else alt_response
            alt_content = extract_json_content(alt_content)
            
            try:
                alt_json = json.loads(alt_content)
                final_reply = alt_json.get("formatted_message", alt_content)
                if len(final_reply) > 180:
                    final_reply = final_reply[:177] + "..."
            except:
                print("Failed to parse alternative response. Using raw text.")
                if len(alt_content) > 180:
                    final_reply = alt_content[:177] + "..."
                else:
                    final_reply = alt_content
            
            print("\nAlternative reply:")
            print(f"\"{final_reply}\"")
            
            alt_approval = sanjay.get_human_input("Do you approve this alternative reply? (yes/no): ").strip().lower()
            if alt_approval != "yes":
                final_reply = sanjay.get_human_input("Please enter your own reply text: ")
                if len(final_reply) > 180:
                    final_reply = final_reply[:177] + "..."
        else:
            final_reply = alternative
            if len(final_reply) > 180:
                final_reply = final_reply[:177] + "..."
    
    # Step 14: Post the reply
    post_confirmation = sanjay.get_human_input(f"Ready to post this reply? (yes/no): ").strip().lower()
    
    if post_confirmation == "yes":
        print("Posting reply...")
        reply_result_json = reply_to_bluesky_wrapper(original_uri=selected_message["did"], reply_content=final_reply)
        reply_result = json.loads(reply_result_json)
        
        if reply_result["status"] == "success":
            print("✅ Reply posted successfully!")
        else:
            print("❌ Error posting reply:", reply_result["message"])
    else:
        print("Reply not posted. Workflow completed.")