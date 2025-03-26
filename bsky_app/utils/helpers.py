import json

def extract_json_content(content_str):
    """Extract JSON content even if wrapped in code fences"""
    if content_str is None:
        return ""
    cleaned = content_str.replace("```json", "").replace("```", "").strip()
    return cleaned

def extract_reply_text_from_raw(raw_content):
    """
    Attempt to extract meaningful text from a raw string response.
    This function uses simple heuristics to find potential reply text.
    """
    cleaned_content = raw_content.replace("```json", "").replace("```", "").strip()
    lines = cleaned_content.splitlines()
    longest_line = max(lines, key=len, default="")
    if len(longest_line) < 10:
        return ""
    return longest_line

def trim_text(text, max_length=180):
    """Trim text to specified length, adding ellipsis if trimmed"""
    if not text or len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."