#!/usr/bin/env python3
"""Test script to verify environment setup"""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

def test_environment():
    """Test environment variables and dependencies"""
    print("🔍 Testing Environment Setup...")
    
    # Test environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = {
        'TELEGRAM_BOT_TOKEN': os.getenv('TELEGRAM_BOT_TOKEN'),
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'ADMIN_USER_ID': os.getenv('ADMIN_USER_ID')
    }
    
    print("\n📋 Environment Variables:")
    all_set = True
    for var, value in required_vars.items():
        status = '✅ Set' if value else '❌ Missing'
        print(f"  {var}: {status}")
        if not value:
            all_set = False
    
    if not all_set:
        print("\n❌ Some required environment variables are missing!")
        return False
    
    # Test imports
    print("\n📦 Testing Dependencies:")
    try:
        import telegram
        print("  python-telegram-bot: ✅")
    except ImportError:
        print("  python-telegram-bot: ❌")
        all_set = False
    
    try:
        import openai
        print("  openai: ✅")
    except ImportError:
        print("  openai: ❌")
        all_set = False
    
    try:
        import aiohttp
        print("  aiohttp: ✅")
    except ImportError:
        print("  aiohttp: ❌")
        all_set = False
    
    # Test optional dependencies
    try:
        import anthropic
        print("  anthropic: ✅ (optional)")
    except ImportError:
        print("  anthropic: ❌ (optional - install if using Claude)")
    
    # Test FFmpeg
    print("\n🎵 Testing FFmpeg:")
    import subprocess
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("  ffmpeg: ✅")
        else:
            print("  ffmpeg: ❌ (install with: brew install ffmpeg)")
            all_set = False
    except FileNotFoundError:
        print("  ffmpeg: ❌ (not found - install with: brew install ffmpeg)")
        all_set = False
    
    # Test project structure
    print("\n📁 Testing Project Structure:")
    base_dir = Path(__file__).parent.parent
    required_dirs = [
        'src/telegram_ai_bot',
        'data',
        'logs',
        'config'
    ]
    
    for dir_path in required_dirs:
        full_path = base_dir / dir_path
        if full_path.exists():
            print(f"  {dir_path}: ✅")
        else:
            print(f"  {dir_path}: ❌")
            full_path.mkdir(parents=True, exist_ok=True)
            print(f"    Created: {dir_path}")
    
    # Test bot token format
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if bot_token:
        if ':' in bot_token and len(bot_token.split(':')[0]) >= 8:
            print(f"\n🤖 Bot Token Format: ✅")
            print(f"  Token starts with: {bot_token[:10]}...")
        else:
            print(f"\n🤖 Bot Token Format: ❌ (invalid format)")
            all_set = False
    
    print(f"\n{'✅ Environment setup complete!' if all_set else '❌ Environment setup incomplete!'}")
    return all_set

def test_configuration():
    """Test configuration loading"""
    print("\n⚙️  Testing Configuration...")
    
    try:
        from telegram_ai_bot.core.config import Config
        Config.validate()
        Config.ensure_directories()
        print("  Configuration: ✅")
        return True
    except Exception as e:
        print(f"  Configuration: ❌ ({e})")
        return False

if __name__ == "__main__":
    env_ok = test_environment()
    config_ok = test_configuration()
    
    if env_ok and config_ok:
        print("\n🎉 All tests passed! You can now run the bot.")
        sys.exit(0)
    else:
        print("\n🚫 Some tests failed. Please fix the issues above.")
        sys.exit(1)