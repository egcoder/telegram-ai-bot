#!/usr/bin/env python3
"""
Test Railway deployment of Telegram AI Bot
"""
import requests
import json
import asyncio
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RailwayDeploymentTester:
    def __init__(self, railway_url: str, bot_token: str = None):
        self.railway_url = railway_url.rstrip('/')
        self.bot_token = bot_token
        self.test_results = []
        
    def test_health_endpoint(self):
        """Test the health check endpoint"""
        logger.info("🩺 Testing health endpoint...")
        
        try:
            response = requests.get(f"{self.railway_url}/health", timeout=10)
            
            if response.status_code == 200:
                self.test_results.append(("Health Endpoint", "✅ PASS", f"Status: {response.status_code}"))
                logger.info("✅ Health endpoint is working")
                return True
            else:
                self.test_results.append(("Health Endpoint", "❌ FAIL", f"Status: {response.status_code}"))
                logger.error(f"❌ Health endpoint failed with status: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.test_results.append(("Health Endpoint", "❌ FAIL", f"Error: {e}"))
            logger.error(f"❌ Health endpoint error: {e}")
            return False
    
    def test_webhook_endpoint(self):
        """Test webhook endpoint (basic connectivity)"""
        logger.info("🔗 Testing webhook endpoint...")
        
        try:
            # Test webhook endpoint with a simple GET request
            response = requests.get(self.railway_url, timeout=10)
            
            # Webhook endpoints typically return 405 for GET requests
            if response.status_code in [200, 405, 404]:
                self.test_results.append(("Webhook Endpoint", "✅ PASS", f"Status: {response.status_code}"))
                logger.info("✅ Webhook endpoint is accessible")
                return True
            else:
                self.test_results.append(("Webhook Endpoint", "❌ FAIL", f"Status: {response.status_code}"))
                logger.error(f"❌ Webhook endpoint issue: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.test_results.append(("Webhook Endpoint", "❌ FAIL", f"Error: {e}"))
            logger.error(f"❌ Webhook endpoint error: {e}")
            return False
    
    def test_telegram_webhook_setup(self):
        """Test if Telegram webhook is properly configured"""
        if not self.bot_token:
            self.test_results.append(("Telegram Webhook", "⏸️ SKIP", "No bot token provided"))
            return None
            
        logger.info("🤖 Testing Telegram webhook configuration...")
        
        try:
            # Get webhook info from Telegram
            response = requests.get(
                f"https://api.telegram.org/bot{self.bot_token}/getWebhookInfo",
                timeout=10
            )
            
            if response.status_code == 200:
                webhook_info = response.json()
                
                if webhook_info.get('ok'):
                    webhook_url = webhook_info['result'].get('url', '')
                    
                    if self.railway_url in webhook_url:
                        self.test_results.append(("Telegram Webhook", "✅ PASS", f"URL: {webhook_url}"))
                        logger.info(f"✅ Telegram webhook configured: {webhook_url}")
                        return True
                    else:
                        self.test_results.append(("Telegram Webhook", "❌ FAIL", f"Wrong URL: {webhook_url}"))
                        logger.error(f"❌ Webhook URL mismatch: {webhook_url}")
                        return False
                else:
                    self.test_results.append(("Telegram Webhook", "❌ FAIL", "API error"))
                    logger.error("❌ Telegram API error")
                    return False
            else:
                self.test_results.append(("Telegram Webhook", "❌ FAIL", f"HTTP {response.status_code}"))
                logger.error(f"❌ Telegram API HTTP error: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.test_results.append(("Telegram Webhook", "❌ FAIL", f"Error: {e}"))
            logger.error(f"❌ Telegram webhook test error: {e}")
            return False
    
    def test_bot_info(self):
        """Test bot information"""
        if not self.bot_token:
            self.test_results.append(("Bot Info", "⏸️ SKIP", "No bot token provided"))
            return None
            
        logger.info("ℹ️ Getting bot information...")
        
        try:
            response = requests.get(
                f"https://api.telegram.org/bot{self.bot_token}/getMe",
                timeout=10
            )
            
            if response.status_code == 200:
                bot_info = response.json()
                
                if bot_info.get('ok'):
                    bot_data = bot_info['result']
                    username = bot_data.get('username', 'N/A')
                    first_name = bot_data.get('first_name', 'N/A')
                    
                    self.test_results.append(("Bot Info", "✅ PASS", f"@{username} ({first_name})"))
                    logger.info(f"✅ Bot info: @{username} ({first_name})")
                    return True
                else:
                    self.test_results.append(("Bot Info", "❌ FAIL", "API error"))
                    return False
            else:
                self.test_results.append(("Bot Info", "❌ FAIL", f"HTTP {response.status_code}"))
                return False
                
        except requests.exceptions.RequestException as e:
            self.test_results.append(("Bot Info", "❌ FAIL", f"Error: {e}"))
            return False
    
    def run_all_tests(self):
        """Run all deployment tests"""
        logger.info("🚀 Starting Railway deployment tests...")
        logger.info(f"🔗 Testing URL: {self.railway_url}")
        
        # Run tests
        self.test_health_endpoint()
        self.test_webhook_endpoint()
        self.test_bot_info()
        self.test_telegram_webhook_setup()
        
        # Print results
        self.print_results()
        
        # Return overall success
        failed_tests = [result for result in self.test_results if "❌ FAIL" in result[1]]
        return len(failed_tests) == 0
    
    def print_results(self):
        """Print test results"""
        logger.info("📊 Test Results:")
        print("\n" + "="*70)
        print("🧪 RAILWAY DEPLOYMENT TEST RESULTS")
        print("="*70)
        
        for test_name, status, details in self.test_results:
            print(f"{status:<15} {test_name:<25} {details}")
        
        print("="*70)
        
        passed = len([r for r in self.test_results if "✅ PASS" in r[1]])
        failed = len([r for r in self.test_results if "❌ FAIL" in r[1]])
        skipped = len([r for r in self.test_results if "⏸️ SKIP" in r[1]])
        
        print(f"📈 SUMMARY: {passed} passed, {failed} failed, {skipped} skipped")
        
        if failed == 0:
            print("🎉 ALL TESTS PASSED! Your bot is ready!")
        else:
            print("⚠️ Some tests failed. Check the issues above.")
        
        print("="*70)

def main():
    """Main test function"""
    # Configuration
    RAILWAY_URL = input("Enter your Railway app URL: ").strip()
    BOT_TOKEN = input("Enter your bot token (optional, press Enter to skip): ").strip()
    
    if not RAILWAY_URL:
        print("❌ Railway URL is required!")
        return
    
    # Initialize tester
    tester = RailwayDeploymentTester(
        railway_url=RAILWAY_URL,
        bot_token=BOT_TOKEN if BOT_TOKEN else None
    )
    
    # Run tests
    success = tester.run_all_tests()
    
    if success:
        print("\n🎯 Next steps:")
        print("1. Test your bot on Telegram by sending messages")
        print("2. Monitor Railway logs for any issues")
        print("3. Check your bot's usage in Railway dashboard")
    else:
        print("\n🔧 Troubleshooting:")
        print("1. Check Railway deployment logs")
        print("2. Verify environment variables are set")
        print("3. Ensure webhook URL is configured properly")

if __name__ == "__main__":
    main()