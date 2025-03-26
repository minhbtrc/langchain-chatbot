# This file is intentionally left mostly empty to avoid circular imports
# Only import what's necessary for basic package initialization
"""LangChain Chatbot backend package."""

__version__ = "1.0.0"

# Expose key components for easier imports
from .config import settings
from .chat.manager import ChatManager
from .api import create_app

__all__ = ["settings", "ChatManager", "create_app"]
