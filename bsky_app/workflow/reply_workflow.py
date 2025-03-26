# filepath: atproto_app/workflow/reply_workflow.py
import json
from utils.helpers import extract_json_content, trim_text
from utils.bluesky import fetch_bluesky_following_wrapper, like_bluesky_wrapper, reply_to_bluesky_wrapper

def show_reply_plan():
    """Display the plan for processing replies"""
    print("\nPlan for Processing Replies:")
    print("Steps:")
    print("  1. The system fetches messages from Bluesky.")
    print("  2. Krsna categorizes messages into political leanings.")
    print("  3. Sanjay displays the messages for you to select one.")
    print("  4. You choose to like and/or reply to the selected message.")
    print("  5. For replies, if agent-generated, Arjunan or Yudhistran is used based on the message's category,")
    print("     then Krsna may edit the reply following tone guidelines, and finally Bheeman posts it.")
    print("Agents Involved:")
    print("  - Sanjay (User Interaction)")
    print("  - Krsna (Categorizer/Editor)")
    print("  - Arjunan / Yudhistran (Responder)")
    print("  - Bheeman (Poster)\n")

def categorize_messages(messages, krsna_agent):
    """Use Krsna to analyze a list of messages for textual intent and tone."""
    if not messages:
        return []
    try:
        # Create a more neutral, safe prompt for message analysis
        message_data = []
        for msg in messages:
            message_data.append({
                "number": msg.get("number", 0),
                "text": msg.get("text", ""),
                "author": msg.get("author", "Unknown")
            })
        
        # Create a more neutral prompt that doesn't trigger content filters
        prompt = json.dumps({
            "task": "analyze",
            "messages": message_data,
            "instruction": (
                "You are Krsna, the analyst. For each message, please provide:\n"
                "1. Analyze the text to determine its general subject matter and overall communication style.\n"
                "2. For each message, assign a category (neutral, informational, opinion, question).\n"
                "Return a JSON array of objects, each with: 'number', 'category', 'subject', and 'style'.\n"
                "Keep your analysis objective and professional."
            )
        })
        
        analysis_result = krsna_agent.generate_reply(messages=[{"role": "user", "content": prompt}])
        
        if isinstance(analysis_result, str):
            analysis_content = analysis_result
        elif isinstance(analysis_result, dict):
            analysis_content = analysis_result.get("content", "")
        else:
            analysis_content = getattr(analysis_result, "content", "")
            
        analysis_content = extract_json_content(analysis_content)
        
        try:
            result_json = json.loads(analysis_content)
            if isinstance(result_json, list):
                analyzed_messages = result_json
            else:
                print("Unexpected analysis format. Using default analysis.")
                analyzed_messages = []
        except json.JSONDecodeError:
            print("Failed to parse analysis result; using default analysis.")
            analyzed_messages = []
            
        # Merge the analysis into each message:
        for msg in messages:
            msg_number = msg.get("number", 0)
            analysis_found = next((am for am in analyzed_messages if am.get("number") == msg_number), None)
            if analysis_found:
                category = analysis_found.get("category", "Not Categorized")
                subject = analysis_found.get("subject", "Unknown Subject")
                style = analysis_found.get("style", "Neutral Style")
                msg["category"] = category
                msg["analysis"] = f"Subject: {subject}, Style: {style}"
            else:
                msg["category"] = "Not Categorized"
                msg["analysis"] = "Not Analyzed"
                
        return messages
        
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        for msg in messages:
            msg["category"] = "Not Categorized"
            msg["analysis"] = "Not Analyzed"
        return messages

def process_reply_workflow(agents):
    """Handle the workflow for replying to messages with improved error handling and agent coordination."""
    # Extract agents
    sanjay = agents["sanjay"]
    krsna = agents["krsna"]
    arjunan = agents["arjunan"]
    yudhistran = agents["yudhistran"]
    
    # Fetch messages from BlueSky
    fetched_messages_json = fetch_bluesky_following_wrapper(limit=20)
    fetched_messages = json.loads(fetched_messages_json)
    if fetched_messages["status"] != "success":
        print("Error fetching messages:", fetched_messages["message"])
        return
    messages = fetched_messages["posts"]
    
    # Categorize messages
    categorization_result = categorize_messages(messages=messages, krsna_agent=krsna)
    if not categorization_result:
        print("Categorization failed; assigning default category 'Not Categorized'.")
        categorized_messages = []
        for msg in messages:
            msg_copy = msg.copy()
            msg_copy["category"] = "Not Categorized"
            categorized_messages.append(msg_copy)
        categorization_result = categorized_messages
    
    # Display messages for selection
    for msg in categorization_result:
        try:
            number = msg.get("number", "?")
            category = msg.get("category", "Not Categorized")
            author = msg.get("author", "Unknown")
            text = msg.get("text", "(No text)")
            did = msg.get("did", "Unknown DID")
            print(f"{number}. [{category}] {author}: {text} (DID: {did})")
        except Exception as e:
            print(f"Error displaying message: {e}", msg)
    
    # Get user selection
    selection = sanjay.get_human_input("Select a message by number (e.g., '1') or type 'skip' to skip: ").strip().lower()
    if selection == "skip":
        print("Skipping reply workflow.")
        return
    
    try:
        selected_number = int(selection.split()[0])
    except ValueError:
        print("Invalid selection format.")
        return
    
    # Find selected message
    selected_message = None
    for msg in categorization_result:
        try:
            if msg.get("number") == selected_number:
                selected_message = msg
                break
        except:
            continue
    
    if not selected_message:
        print("Invalid selection.")
        return
    
    # Like option
    like_option = sanjay.get_human_input("Would you like to like this message? (yes/no): ").strip().lower()
    if like_option == "yes":
        like_result_json = like_bluesky_wrapper(post_uri=selected_message["did"])
        like_result = json.loads(like_result_json)
        if like_result["status"] == "success":
            print("Message liked successfully.")
        else:
            print("Error liking message:", like_result["message"])
    
    # Reply option
    reply_option = sanjay.get_human_input("Would you like to reply to this message? (yes/no): ").strip().lower()
    if reply_option != "yes":
        print("No reply will be created. Workflow completed.")
        return
    
    # Get reply type
    reply_type = sanjay.get_human_input("Type 'human' to reply yourself or 'agent' for agent-generated reply: ").strip().lower()
    
    if reply_type == "human":
        # Human generated reply
        reply_text = sanjay.get_human_input("Enter your reply text: ")
    elif reply_type == "agent":
        # NEW WORKFLOW: Enhanced categorization for message political leaning
        categorize_prompt = json.dumps({
            "task": "political_analysis",
            "message": selected_message["text"],
            "instruction": (
                "Analyze this message and determine its political leaning on a scale: "
                "'far-left', 'left', 'middle', 'right', or 'far-right'. "
                "Consider the content, tone, and perspective. "
                "Return a JSON object with keys: 'category' and 'reasoning'."
            )
        })
        
        # Get categorization from Krsna
        categorization = krsna.generate_reply(messages=[{"role": "user", "content": categorize_prompt}])
        if isinstance(categorization, str):
            cat_content = categorization
        elif isinstance(categorization, dict):
            cat_content = categorization.get("content", "")
        else:
            cat_content = getattr(categorization, "content", "")
        cat_content = extract_json_content(cat_content)
        
        # Parse categorization
        try:
            cat_json = json.loads(cat_content)
            category = cat_json.get("category", "middle")
            reasoning = cat_json.get("reasoning", "No reasoning provided")
            print(f"Message categorized as: {category}")
            print(f"Reasoning: {reasoning}")
        except:
            print("Categorization parsing failed. Defaulting to 'middle'.")
            category = "middle"
        
        # Select appropriate agent based on political leaning
        if category.lower() == "far-right":
            print("Message categorized as 'far-right'. Using Yudhistran for a soothing, middle-ground response.")
            agent_prompt = json.dumps({
                "task": "reply",
                "message": selected_message["text"],
                "instruction": (
                    "You are Yudhistran, the balanced mediator. This message appears to have 'far-right' views. "
                    "Craft a measured, soothing response that finds middle ground while maintaining respect. "
                    "Aim for exactly 180 characters and return your response in a JSON object with key "
                    "'formatted_message'."
                )
            })
            reply_agent = yudhistran
        else:
            print(f"Message categorized as '{category}'. Using Arjunan for a response.")
            agent_prompt = json.dumps({
                "task": "reply",
                "message": selected_message["text"],
                "instruction": (
                    "You are Arjunan. This message has been categorized as having " + category + " political views. "
                    "Craft a thoughtful, assertive response in exactly 180 characters. "
                    "Return your response in a JSON object with key 'formatted_message'."
                )
            })
            reply_agent = arjunan
        
        # Generate the reply with the selected agent
        print(f"Generating response with {reply_agent.name}...")
        agent_response = reply_agent.generate_reply(messages=[{"role": "user", "content": agent_prompt}])
        if isinstance(agent_response, str):
            reply_content = agent_response
        elif isinstance(agent_response, dict):
            reply_content = agent_response.get("content", "")
        else:
            reply_content = getattr(agent_response, "content", "")
        reply_content = extract_json_content(reply_content)
        
        # Parse the reply
        try:
            reply_json = json.loads(reply_content)
            reply_text = reply_json.get("formatted_message", "")
            
            # FIX: Safely handle dictionary values
            if not reply_text:
                for field in ["final_reply", "reply", "analyzed_reply", "message", "text", "content"]:
                    if field in reply_json:
                        candidate = reply_json.get(field, "")
                        # Check if candidate is a string before calling lower()
                        if isinstance(candidate, str):
                            if candidate.lower() not in ["progressive", "liberal", "centrist", "conservative",
                                                        "strongly conservative", "left", "right", "far-left", "far-right"]:
                                reply_text = candidate
                                break
                        elif isinstance(candidate, dict):
                            # Handle dictionary case
                            if 'text' in candidate:
                                reply_text = candidate['text']
                                break
            
            if not reply_text:
                print("No suitable reply field found. Using raw agent response.")
                reply_text = reply_content
        except Exception as e:
            print(f"Reply parsing failed: {e}")
            reply_text = reply_content
        
        # Send to Krsna for validation
        validate_prompt = json.dumps({
            "task": "validate_response",
            "original_message": selected_message["text"],
            "agent_response": reply_text,
            "instruction": (
                "As Krsna, evaluate if this response is appropriate, respectful, and fits within 180 characters. "
                "Return a JSON object with keys: 'valid' (boolean), 'edited_response' (string), and 'feedback' (string)."
            )
        })
        
        print("Sending to Krsna for validation...")
        validation = krsna.generate_reply(messages=[{"role": "user", "content": validate_prompt}])
        if isinstance(validation, str):
            valid_content = validation
        elif isinstance(validation, dict):
            valid_content = validation.get("content", "")
        else:
            valid_content = getattr(validation, "content", "")
        valid_content = extract_json_content(valid_content)
        
        # Process validation results
        try:
            valid_json = json.loads(valid_content)
            is_valid = valid_json.get("valid", False)
            validation_feedback = valid_json.get("feedback", "No feedback provided")
            if is_valid:
                edited_reply = valid_json.get("edited_response", reply_text)
                print("✅ Krsna has validated the reply as appropriate.")
            else:
                edited_reply = valid_json.get("edited_response", reply_text)
                print("⚠️ Krsna has concerns about the reply and has edited it.")
            print(f"Feedback: {validation_feedback}")
        except Exception as e:
            print(f"Validation parsing failed: {e}")
            edited_reply = reply_text
            print("Using original agent response without validation.")
    else:
        print("Invalid reply type. Reply cancelled.")
        return
    
    # Ensure the reply is within length limits
    edited_reply = trim_text(edited_reply, 180)
    
    # Show final reply to user and get approval
    print("\nFinal reply message:")
    print(f"\"{edited_reply}\"")
    approval = sanjay.get_human_input("Are you satisfied with this reply? (yes/no): ").strip().lower()
    
    # If user is not satisfied, ask Krsna for a fair alternative
    if approval != "yes":
        print("You're not satisfied with the reply. Asking Krsna for an alternative...")
        
        fair_prompt = json.dumps({
            "task": "fair_response",
            "original_message": selected_message["text"],
            "instruction": (
                "As Krsna, please provide a fair and balanced reply to this message. "
                "The previous reply was not satisfactory to the user. "
                "Create a thoughtful response in exactly 180 characters that is politically balanced "
                "and respectful. Return as JSON with key 'formatted_message'."
            )
        })
        
        fair_response = krsna.generate_reply(messages=[{"role": "user", "content": fair_prompt}])
        if isinstance(fair_response, str):
            fair_content = fair_response
        elif isinstance(fair_response, dict):
            fair_content = fair_response.get("content", "")
        else:
            fair_content = getattr(fair_response, "content", "")
        fair_content = extract_json_content(fair_content)
        
        try:
            fair_json = json.loads(fair_content)
            fair_reply = fair_json.get("formatted_message", "")
            if not fair_reply:
                # Try other common field names
                for field in ["response", "reply", "message", "text", "content"]:
                    if field in fair_json and isinstance(fair_json[field], str):
                        fair_reply = fair_json[field]
                        break
        except:
            fair_reply = fair_content if len(fair_content) < 180 else fair_content[:177] + "..."
        
        # Show the fair reply and get approval again
        fair_reply = trim_text(fair_reply, 180)
        print("\nKrsna's alternative reply:")
        print(f"\"{fair_reply}\"")
        final_approval = sanjay.get_human_input("Do you approve this alternative reply? (yes/no): ").strip().lower()
        
        if final_approval == "yes":
            edited_reply = fair_reply
        else:
            custom_reply = sanjay.get_human_input("Please provide your own reply text: ").strip()
            edited_reply = trim_text(custom_reply, 180)
    
    # Final confirmation to post
    post_confirmation = sanjay.get_human_input(f"Ready to post this reply? (yes/no): ").strip().lower()
    
    if post_confirmation == "yes":
        print("Sending reply to Bluesky...")
        # Post the reply
        reply_result_json = reply_to_bluesky_wrapper(original_uri=selected_message["did"], reply_content=edited_reply)
        reply_result = json.loads(reply_result_json)
        
        if reply_result.get("status") == "success":
            print("✅ Reply posted successfully!")
        else:
            print("❌ Error posting reply:", reply_result.get("message"))
    else:
        print("Reply not posted. Workflow completed.")