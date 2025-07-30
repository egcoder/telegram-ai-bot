# 🚂 Railway Deployment - Complete Guide

## ✅ Step 1: Push to GitHub (COMPLETED ✅)

The code has been successfully pushed to:
**https://github.com/egcoder/telegram-ai-bot**

## ✅ Step 2: Deploy to Railway

### Railway Setup:
1. Go to https://railway.app
2. Click **"Login with GitHub"**
3. Authorize Railway to access your GitHub
4. Click **"New Project"**
5. Select **"Deploy from GitHub repo"**
6. Choose **`egcoder/telegram-ai-bot`**
7. Railway will automatically start building

## ✅ Step 3: Configure Environment Variables

In Railway dashboard → **Variables** tab → **Add Variable**:

```bash
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
OPENAI_API_KEY=your_openai_api_key_here
ADMIN_USER_ID=your_telegram_user_id
ANTHROPIC_API_KEY=your_anthropic_api_key_here
LOG_LEVEL=INFO
```

**Note**: Use your actual API keys from your .env file (not the placeholder values above)

## ✅ Step 4: Add PostgreSQL Database

1. In Railway dashboard → **Add Service**
2. Select **PostgreSQL**
3. Railway automatically sets `DATABASE_URL`

## ✅ Step 5: Deploy & Test

1. Railway automatically deploys after environment variables are set
2. Check **Deployments** tab for build logs
3. Your bot will be available at: `https://your-app.railway.app`

## ✅ Step 6: Test Your Bot

### Test Commands:
1. Open Telegram
2. Search for your bot: `@your_bot_name_bot`
3. Send: `/start`
4. Send: `/help`
5. Send a voice message
6. Check if responses work

### Check Webhook:
```bash
curl https://your-app.railway.app/health
```

## 🔍 Troubleshooting

### Check Railway Logs:
1. Railway dashboard → **Deployments** tab
2. Click on latest deployment
3. Check build and runtime logs

### Common Issues:
- **Bot not responding**: Check environment variables
- **Build failed**: Check requirements.txt
- **Webhook errors**: Check Railway logs for webhook setup

## 📊 Expected Costs:
- **Railway**: ~$5-10/month
- **OpenAI API**: ~$10-30/month (usage-based)
- **Total**: ~$15-40/month

## 🎉 Success Indicators:
- ✅ Railway deployment shows "Success"
- ✅ Bot responds to `/start` command
- ✅ Voice messages are processed
- ✅ No errors in Railway logs
- ✅ Webhook endpoint returns 200 OK

Your bot is now live and ready to use! 🚀