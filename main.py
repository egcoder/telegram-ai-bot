#!/usr/bin/env python3
"""
Main entry point for the Telegram AI Bot

This script provides a convenient way to run the bot from the project root.
"""
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

if __name__ == "__main__":
    from telegram_ai_bot.__main__ import main
    import asyncio
    
    asyncio.run(main())