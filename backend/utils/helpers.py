# utils/helpers.py
# This file contains helper functions for text cleaning, formatting, and utility tasks

import re
import os


def clean_text(text: str) -> str:
    """
    Cleans and normalizes text by removing extra whitespace and fixing formatting.
    
    Args:
        text: Raw text to clean
    
    Returns:
        Cleaned text
    """
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncates text to a maximum length and adds a suffix.
    Useful for displaying long answers in a compact way.
    
    Args:
        text: Text to truncate
        max_length: Maximum length before truncating
        suffix: Text to add at the end (default: "...")
    
    Returns:
        Truncated text
    """
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length] + suffix


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Formats a decimal value as a percentage string.
    
    Args:
        value: Value between 0 and 1 (or 0-100)
        decimals: Number of decimal places
    
    Returns:
        Formatted percentage string
    """
    
    if value > 1:
        value = value / 100
    
    percentage = value * 100
    return f"{percentage:.{decimals}f}%"


def ensure_directory_exists(directory_path: str) -> None:
    """
    Creates a directory if it doesn't already exist.
    
    Args:
        directory_path: Path to the directory
    """
    
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"📁 Created directory: {directory_path}")


def remove_special_characters(text: str) -> str:
    """
    Removes special characters from text, keeping only alphanumeric and basic punctuation.
    Useful for cleaning transcribed audio.
    
    Args:
        text: Text to clean
    
    Returns:
        Text with special characters removed
    """
    
    # Keep alphanumeric, spaces, and common punctuation (. , ? ! - ')
    text = re.sub(r"[^a-zA-Z0-9\s.,'?!\-]", "", text)
    
    return text


def split_into_sentences(text: str) -> list:
    """
    Splits text into individual sentences.
    
    Args:
        text: Text to split
    
    Returns:
        List of sentences
    """
    
    # Split by common sentence endings
    sentences = re.split(r'[.!?]+', text)
    
    # Clean up and filter empty sentences
    sentences = [s.strip() for s in sentences if s.strip()]
    
    return sentences


def highlight_differences(correct: str, user: str) -> str:
    """
    Highlights the differences between two strings.
    Useful for showing what the user got wrong.
    
    Args:
        correct: The correct text
        user: The user's text
    
    Returns:
        Formatted string showing differences
    """
    
    # Simple character-by-character comparison
    diff_text = ""
    
    for i, (c, u) in enumerate(zip(correct, user)):
        if c == u:
            diff_text += c
        else:
            diff_text += f"[{u}→{c}]"
    
    # Add any extra characters from correct answer
    if len(correct) > len(user):
        diff_text += f" [missing: {correct[len(user):]}]"
    
    # Add any extra characters from user answer
    elif len(user) > len(correct):
        diff_text += f" [extra: {user[len(correct):]}]"
    
    return diff_text


def get_file_size_mb(file_path: str) -> float:
    """
    Gets the file size in megabytes.
    
    Args:
        file_path: Path to the file
    
    Returns:
        File size in MB
    """
    
    if not os.path.exists(file_path):
        return 0.0
    
    size_bytes = os.path.getsize(file_path)
    size_mb = size_bytes / (1024 * 1024)
    
    return round(size_mb, 2)


def format_time(seconds: int) -> str:
    """
    Formats seconds into a readable time string.
    
    Args:
        seconds: Number of seconds
    
    Returns:
        Formatted time string (e.g., "1m 30s")
    """
    
    minutes = seconds // 60
    secs = seconds % 60
    
    if minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"