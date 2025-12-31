# Streamlit App Deployment Guide

## Quick Deploy to Streamlit Cloud

### Prerequisites
- GitHub account (you already have this: faraaz-bot/trade)
- Streamlit Cloud account (free at https://streamlit.io/cloud)

### Step-by-Step Deployment

#### 1. Sign Up for Streamlit Cloud
1. Go to https://share.streamlit.io/
2. Click "Sign up" or "Continue with GitHub"
3. Authorize Streamlit to access your GitHub repositories

#### 2. Deploy Your App
1. Click "New app" button
2. Select your repository: `faraaz-bot/trade`
3. Select branch: `main`
4. Main file path: `app.py`
5. Click "Deploy!"

#### 3. App Configuration
The app will automatically use:
- `requirements.txt` - All dependencies will be installed
- `.streamlit/config.toml` - Theme and server configuration

### Deployment Options

#### Option 1: Main Trading Dashboard (Recommended)
- **File:** `app.py`
- **Features:** 
  - Backtest runner
  - 4 interactive charts
  - Trade analysis
  - CSV export
- **URL:** Will be `https://[your-app-name].streamlit.app`

#### Option 2: TradingView-Style Dashboard
- **File:** `dashboards/trading_dashboard.py`
- **Features:**
  - Professional dark theme
  - 4-panel technical charts
  - Trade filtering
  - Historical analysis
- **URL:** Will be `https://[your-app-name].streamlit.app`

### Multiple Apps Deployment

You can deploy both apps separately:

1. **First App (Main Dashboard):**
   - Repository: faraaz-bot/trade
   - Branch: main
   - Main file: `app.py`
   - App name: `momentum-hod-strategy`

2. **Second App (TradingView Dashboard):**
   - Repository: faraaz-bot/trade
   - Branch: main
   - Main file: `dashboards/trading_dashboard.py`
   - App name: `momentum-hod-charts`

### Environment Variables (Optional)

If you need to add any API keys or secrets:
1. Go to your app settings in Streamlit Cloud
2. Click "Secrets"
3. Add your secrets in TOML format

### Post-Deployment

After deployment:
1. Your app will be live at: `https://[your-app-name].streamlit.app`
2. Share the URL with anyone
3. App will auto-update when you push to GitHub
4. Free tier includes: Unlimited public apps, 1GB resources per app

### Troubleshooting

#### App won't start
- Check the logs in Streamlit Cloud dashboard
- Verify all dependencies in requirements.txt
- Ensure no local file paths are hardcoded

#### Missing data
- The app needs `backtest_results.csv` to display trades
- Run the backtest first or include sample data

#### Slow loading
- First load may take 30-60 seconds
- Subsequent loads are faster due to caching

### Local Testing Before Deploy

Test locally first:
```bash
streamlit run app.py
```

Or for the TradingView dashboard:
```bash
streamlit run dashboards/trading_dashboard.py
```

### Updating Your Deployed App

Simply push changes to GitHub:
```bash
git add .
git commit -m "Update app"
git push origin main
```

Streamlit Cloud will automatically redeploy!

### Custom Domain (Optional)

Streamlit Cloud allows custom domains on paid plans:
1. Go to app settings
2. Click "Custom domain"
3. Follow instructions to configure DNS

---

## Alternative Deployment Options

### Deploy to Heroku
1. Create `Procfile`:
   ```
   web: streamlit run app.py --server.port=$PORT
   ```
2. Deploy via Heroku CLI or GitHub integration

### Deploy to AWS/GCP/Azure
Use Docker container:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py"]
```

---

## Support

For issues:
- Streamlit Docs: https://docs.streamlit.io/
- Community Forum: https://discuss.streamlit.io/
- GitHub Issues: https://github.com/faraaz-bot/trade/issues
