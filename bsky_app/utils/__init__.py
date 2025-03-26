"""
Utility functions for the ATProto application.
"""

# Import and expose key functions from the utility modules
from .bluesky import (
    bluesky_login,
    post_to_bluesky,
    like_bluesky,
    reply_to_bluesky,
    fetch_bluesky_following,
    post_to_bluesky_wrapper,
    like_bluesky_wrapper,
    reply_to_bluesky_wrapper,
    fetch_bluesky_following_wrapper
)

from .helpers import (
    extract_json_content,
    extract_reply_text_from_raw,
    trim_text
)

# Define what's available when using `from atproto_app.utils import *`
__all__ = [
    # Bluesky functions
    'bluesky_login',
    'post_to_bluesky',
    'like_bluesky',
    'reply_to_bluesky',
    'fetch_bluesky_following',
    'post_to_bluesky_wrapper',
    'like_bluesky_wrapper',
    'reply_to_bluesky_wrapper',
    'fetch_bluesky_following_wrapper',
    
    # Helper functions
    'extract_json_content',
    'extract_reply_text_from_raw',
    'trim_text'
]