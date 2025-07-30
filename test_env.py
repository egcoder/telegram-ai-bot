from dotenv import load_dotenv
import os

load_dotenv()

print("🔍 Checking environment variables...")
print(f"TELEGRAM_BOT_TOKEN: {'✅ Set' if os.getenv('TELEGRAM_BOT_TOKEN') else '❌ Missing'}")
print(f"OPENAI_API_KEY: {'✅ Set' if os.getenv('OPENAI_API_KEY') else '❌ Missing'}")
print(f"ADMIN_USER_ID: {'✅ Set' if os.getenv('ADMIN_USER_ID') else '❌ Missing'}")

if os.getenv('TELEGRAM_BOT_TOKEN'):
    print(f"Bot token starts with: {os.getenv('TELEGRAM_BOT_TOKEN')[:10]}...")