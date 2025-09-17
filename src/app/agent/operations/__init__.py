"""
Operations package - Pluggable function modules for the SmartAgent.

This package contains modular operation functions that can be dynamically loaded
and registered with the agent. Each operation module should export functions
that can be easily plugged into the agent's function calling system.

Architecture:
- Each operation module (e.g. app_operations.py, system_operations.py) contains
  specific functionality and exports a get_functions() method
- The agent automatically discovers and loads all modules listed in AVAILABLE_OPERATIONS
- New operation types can be added by simply creating a new module and adding it to the list
- No changes needed to the main agent code - fully pluggable

Adding New Operations:
1. Create a new .py file in this directory (e.g. media_operations.py)
2. Define your functions and wrap them with AIFunction
3. Export a get_functions() method that returns the list of AIFunction objects
4. Add the module to AVAILABLE_OPERATIONS list below
5. That's it! The agent will automatically discover and register the functions
"""

# Import available operation modules
from . import app_operations
from . import system_operations

# List of available operation modules for dynamic loading
# Add new operation modules here to make them available to the agent
AVAILABLE_OPERATIONS = [
    app_operations,
    system_operations,
    # Add new operation modules here:
    # media_operations,
    # file_operations, 
    # network_operations,
    # etc.
]

def get_all_functions():
    """
    Get all available functions from all operation modules.
    
    Returns:
        List of AIFunction objects that can be registered with Kani
    """
    functions = []
    
    for module in AVAILABLE_OPERATIONS:
        if hasattr(module, 'get_functions'):
            functions.extend(module.get_functions())
    
    return functions