"""
System operations module - Basic system utility functions.
"""

import os
import datetime
import psutil
from typing import Dict, Any, List
from kani import AIFunction

def get_current_time() -> str:
    """
    Get the current date and time.
    
    Returns:
        Current date and time as a formatted string
    """
    try:
        now = datetime.datetime.now()
        return now.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        return f"Error getting current time: {str(e)}"

def get_working_directory() -> str:
    """
    Get the current working directory.
    
    Returns:
        Current working directory path
    """
    try:
        return os.getcwd()
    except Exception as e:
        return f"Error getting working directory: {str(e)}"

def list_directory(path: str = ".") -> str:
    """
    List contents of a directory.
    
    Args:
        path: Directory path to list (defaults to current directory)
        
    Returns:
        String listing directory contents
    """
    try:
        if not os.path.exists(path):
            return f"Directory does not exist: {path}"
            
        items = os.listdir(path)
        if not items:
            return f"Directory is empty: {path}"
            
        result = f"Contents of {path}:\n"
        for item in sorted(items):
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                result += f"📁 {item}/\n"
            else:
                result += f"📄 {item}\n"
                
        return result
        
    except Exception as e:
        return f"Error listing directory {path}: {str(e)}"

def get_memory_usage() -> str:
    """
    Get current system memory usage.
    
    Returns:
        Memory usage information as a string
    """
    try:
        memory = psutil.virtual_memory()
        
        total = memory.total / (1024**3)  # Convert to GB
        available = memory.available / (1024**3)
        used = memory.used / (1024**3)
        percent = memory.percent
        
        result = f"Memory Usage:\n"
        result += f"Total: {total:.2f} GB\n"
        result += f"Used: {used:.2f} GB\n"
        result += f"Available: {available:.2f} GB\n"
        result += f"Usage: {percent:.1f}%"
        
        return result
        
    except Exception as e:
        return f"Error getting memory usage: {str(e)}"

def get_disk_usage(path: str = ".") -> str:
    """
    Get disk usage for a given path.
    
    Args:
        path: Path to check disk usage for
        
    Returns:
        Disk usage information as a string
    """
    try:
        if not os.path.exists(path):
            return f"Path does not exist: {path}"
            
        disk_usage = psutil.disk_usage(path)
        
        total = disk_usage.total / (1024**3)  # Convert to GB
        used = disk_usage.used / (1024**3)
        free = disk_usage.free / (1024**3)
        percent = (used / total) * 100
        
        result = f"Disk Usage for {path}:\n"
        result += f"Total: {total:.2f} GB\n"
        result += f"Used: {used:.2f} GB\n"
        result += f"Free: {free:.2f} GB\n"
        result += f"Usage: {percent:.1f}%"
        
        return result
        
    except Exception as e:
        return f"Error getting disk usage for {path}: {str(e)}"

def open_url(url: str) -> str:
    """
    Open a URL in the default browser.
    
    Args:
        url: URL to open
        
    Returns:
        Success or error message
    """
    try:
        import webbrowser
        webbrowser.open(url)
        return f"Successfully opened {url} in default browser"
    except Exception as e:
        return f"Failed to open URL {url}: {str(e)}"

def search_web(query: str) -> str:
    """
    Search the web using the default browser.
    
    Args:
        query: Search query
        
    Returns:
        Success or error message
    """
    try:
        import webbrowser
        import urllib.parse
        
        # Create Google search URL
        encoded_query = urllib.parse.quote_plus(query)
        search_url = f"https://www.google.com/search?q={encoded_query}"
        
        webbrowser.open(search_url)
        return f"Successfully searched for '{query}' in default browser"
    except Exception as e:
        return f"Failed to search for '{query}': {str(e)}"

# Define AI functions for Kani
get_current_time_function = AIFunction(
    get_current_time,
    name="get_current_time",
    desc="Get the current date and time."
)

get_working_directory_function = AIFunction(
    get_working_directory,
    name="get_working_directory",
    desc="Get the current working directory path."
)

list_directory_function = AIFunction(
    list_directory,
    name="list_directory",
    desc="List the contents of a directory. Takes an optional path parameter."
)

get_memory_usage_function = AIFunction(
    get_memory_usage,
    name="get_memory_usage",
    desc="Get current system memory usage information."
)

get_disk_usage_function = AIFunction(
    get_disk_usage,
    name="get_disk_usage", 
    desc="Get disk usage information for a given path."
)

open_url_function = AIFunction(
    open_url,
    name="open_url",
    desc="Open any URL in the default browser."
)

search_web_function = AIFunction(
    search_web,
    name="search_web",
    desc="Search the web using Google. Just provide the search query."
)

def get_functions() -> List[AIFunction]:
    """Get all AI functions from this module."""
    return [
        get_current_time_function,
        get_working_directory_function,
        list_directory_function,
        get_memory_usage_function,
        get_disk_usage_function,
        open_url_function,
        search_web_function
    ]