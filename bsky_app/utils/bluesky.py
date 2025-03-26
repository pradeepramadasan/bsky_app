import os
import json
import mimetypes
import atproto
from config import BLUESKY_USERNAME, BLUESKY_PASSWORD  # Changed from ..config to config

# Rest of your file remains unchanged
def bluesky_login(username=None, password=None):
    """Login to Bluesky"""
    client = atproto.Client()
    client.login(username or BLUESKY_USERNAME, password or BLUESKY_PASSWORD)
    return client
def post_to_bluesky(message, image_path=None):
    """Post content to Bluesky, optionally with an image."""
    try:
        client = bluesky_login()
        if image_path:
            mime_type = mimetypes.guess_type(image_path)[0]
            if not mime_type:
                mime_type = "image/jpeg"
            with open(image_path, "rb") as f:
                image_binary = f.read()
            upload_response = client.com.atproto.repo.upload_blob(image_binary, mime_type)
            blob = upload_response.blob
            client.send_post(
                text=message,
                embed={
                    '$type': 'app.bsky.embed.images',
                    'images': [{
                        'alt': 'Image shared by AI agent',
                        'image': blob
                    }]
                }
            )
            return {"status": "success", "message": "Posted with image successfully"}
        else:
            client.send_post(text=message)
            return {"status": "success", "message": "Posted successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def like_bluesky(post_uri):
    """Like a post on Bluesky identified by its URI."""
    try:
        client = bluesky_login()
        parts = post_uri.split('/')
        if len(parts) < 5:
            return {"status": "error", "message": "Invalid post URI format"}
        response = client.app.bsky.feed.get_posts({"uris": [post_uri]})
        if not response.posts:
            return {"status": "error", "message": "Post not found."}
        post = response.posts[0]
        client.like(uri=post_uri, cid=post.cid)
        return {"status": "success", "message": "Post liked successfully"}
    except Exception as e:
        return {"status": "error", "message": f"Error: {str(e)}"}

def reply_to_bluesky(original_uri, reply_content):
    """Post a reply to a given message on Bluesky identified by its URI."""
    try:
        client = bluesky_login()
        parts = original_uri.split('/')
        if len(parts) < 5:
            return {"status": "error", "message": "Invalid original URI format"}
        did = parts[2]
        rkey = parts[-1]
        response = client.app.bsky.feed.get_posts({"uris": [original_uri]})
        if not response.posts:
            return {"status": "error", "message": "Original post not found."}
        original_post = response.posts[0]
        client.send_post(
            text=reply_content,
            reply_to={
                "root": {"uri": original_uri, "cid": original_post.cid},
                "parent": {"uri": original_uri, "cid": original_post.cid}
            }
        )
        return {"status": "success", "message": "Reply posted successfully"}
    except Exception as e:
        return {"status": "error", "message": f"Error: {str(e)}"}

def fetch_bluesky_following(limit=20):
    """Fetch the latest posts from accounts the user is following on Bluesky."""
    try:
        client = bluesky_login()
        timeline = client.get_timeline(limit=limit)
        posts = []
        for idx, feed_view in enumerate(timeline.feed, start=1):
            post = feed_view.post
            posts.append({
                "number": idx,
                "did": post.uri,
                "author": post.author.display_name or post.author.handle,
                "text": post.record.text,
                "timestamp": post.indexed_at
            })
        return {"status": "success", "posts": posts}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Wrapper functions that return JSON strings
def post_to_bluesky_wrapper(message, image_path=None):
    """Wrapper for post_to_bluesky that returns JSON string instead of dict"""
    result = post_to_bluesky(message, image_path)
    return json.dumps(result)

def like_bluesky_wrapper(post_uri):
    """Wrapper for like_bluesky that returns JSON string instead of dict"""
    result = like_bluesky(post_uri=post_uri)
    return json.dumps(result)

def reply_to_bluesky_wrapper(original_uri, reply_content):
    """Wrapper for reply_to_bluesky that returns JSON string instead of dict"""
    result = reply_to_bluesky(original_uri=original_uri, reply_content=reply_content)
    return json.dumps(result)

def fetch_bluesky_following_wrapper(limit=20):
    """Wrapper for fetch_bluesky_following that returns JSON string"""
    result = fetch_bluesky_following(limit)
    return json.dumps(result)