"""Version information for the Telegram AI Bot"""

# Deployment version - increment this when making fixes
DEPLOY_VERSION = "1.1.4"
DEPLOY_DATE = "2024-01-31"
FIXES = [
    "1.1.4 - Use subprocess isolation to completely avoid parameter pollution",
    "1.1.3 - Fixed UnboundLocalError and added 30s timeout to prevent hanging",
    "1.1.2 - Improved error handling and OpenAI version detection",
    "1.1.1 - Fixed import scope error in error handler",
    "1.1.0 - Fixed Whisper API response_format error with isolated service",
    "1.0.0 - Initial deployment"
]