# Deployment Troubleshooting Guide

## 🔧 Common Deployment Errors & Solutions

### Error: 404 NOT_FOUND

**Possible Causes:**
1. Missing deployment files
2. Incorrect build/start commands
3. Wrong directory structure
4. Missing dependencies

**Solutions:**

#### ✅ Solution 1: Verify Required Files
Make sure these files exist:
- `backend/requirements.txt` (with gunicorn, eventlet, psycopg2-binary)
- `Procfile` (for Heroku/Render)
- `render.yaml` (for Render.com)
- `backend/run.py` (entry point)

#### ✅ Solution 2: Update Requirements
```bash
cd backend
pip install gunicorn eventlet psycopg2-binary
pip freeze > requirements.txt
```

#### ✅ Solution 3: Test Locally with Gunicorn
```bash
cd backend
gunicorn -k eventlet -w 1 -b 0.0.0.0:5000 run:app
```

If this works locally, deployment should work too.

---

## 🚀 Render.com Deployment Steps

### Method 1: Using render.yaml (Recommended)

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Add deployment configuration"
   git push origin main
   ```

2. **Connect to Render**
   - Go to https://render.com
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Render will auto-detect `render.yaml`
   - Click "Apply"

3. **Wait for Deployment**
   - Backend: ~5-10 minutes
   - Database: ~2-3 minutes
   - Frontend: ~3-5 minutes

### Method 2: Manual Setup

#### Backend:
1. New Web Service
2. Connect GitHub repo
3. Settings:
   ```
   Name: ipl-auction-backend
   Environment: Python 3
   Build Command: cd backend && pip install -r requirements.txt && python init_db.py
   Start Command: cd backend && gunicorn -k eventlet -w 1 --bind 0.0.0.0:$PORT run:app
   ```
4. Environment Variables:
   ```
   FLASK_ENV=production
   SECRET_KEY=<generate-random-string>
   DATABASE_URL=<from-postgres-service>
   CORS_ORIGINS=*
   ```

#### Database:
1. New PostgreSQL
2. Name: ipl-auction-db
3. Copy Internal Database URL
4. Add to backend as DATABASE_URL

#### Frontend:
1. New Static Site
2. Settings:
   ```
   Build Command: cd frontend && npm install && npm run build
   Publish Directory: frontend/dist
   ```
3. Environment Variables:
   ```
   VITE_API_URL=<your-backend-url>
   ```

---

## 🐛 Debugging Deployment Issues

### Check Render Logs

1. Go to your service dashboard
2. Click "Logs" tab
3. Look for error messages

### Common Log Errors:

#### "ModuleNotFoundError: No module named 'gunicorn'"
**Fix:** Add gunicorn to requirements.txt
```bash
echo "gunicorn==21.2.0" >> backend/requirements.txt
```

#### "ModuleNotFoundError: No module named 'eventlet'"
**Fix:** Add eventlet to requirements.txt
```bash
echo "eventlet==0.33.3" >> backend/requirements.txt
```

#### "ModuleNotFoundError: No module named 'psycopg2'"
**Fix:** Add psycopg2-binary to requirements.txt
```bash
echo "psycopg2-binary==2.9.9" >> backend/requirements.txt
```

#### "Error: Cannot find module 'run'"
**Fix:** Ensure run.py exists in backend/ and exports app
```python
# backend/run.py
from app import create_app, socketio
app = create_app()
```

#### "Database connection failed"
**Fix:** 
1. Ensure DATABASE_URL is set correctly
2. Use PostgreSQL, not SQLite in production
3. Check database is running

---

## 🔍 Testing Deployment Locally

### Test with Production Settings

1. **Install production dependencies:**
   ```bash
   cd backend
   pip install gunicorn eventlet psycopg2-binary
   ```

2. **Set environment variables:**
   ```bash
   # Windows
   set FLASK_ENV=production
   set DATABASE_URL=sqlite:///auction.db
   
   # Linux/Mac
   export FLASK_ENV=production
   export DATABASE_URL=sqlite:///auction.db
   ```

3. **Run with Gunicorn:**
   ```bash
   gunicorn -k eventlet -w 1 -b 0.0.0.0:5000 run:app
   ```

4. **Test the API:**
   ```bash
   curl http://localhost:5000/api/players
   ```

If this works, your deployment configuration is correct!

---

## 📋 Pre-Deployment Checklist

- [ ] `backend/requirements.txt` includes:
  - gunicorn
  - eventlet
  - psycopg2-binary
  - All other dependencies

- [ ] `Procfile` exists with correct command

- [ ] `backend/run.py` exports `app` variable

- [ ] `.gitignore` excludes:
  - `__pycache__/`
  - `*.pyc`
  - `.env`
  - `*.db`
  - `node_modules/`

- [ ] Environment variables configured:
  - FLASK_ENV=production
  - SECRET_KEY
  - DATABASE_URL
  - CORS_ORIGINS

- [ ] Database initialization script works:
  ```bash
  python backend/init_db.py
  ```

- [ ] Frontend build works:
  ```bash
  cd frontend
  npm install
  npm run build
  ```

---

## 🆘 Still Having Issues?

### Option 1: Deploy to Heroku Instead

Heroku might be easier if Render is giving issues:

```bash
# Install Heroku CLI
# Then:
cd backend
heroku create ipl-auction-backend
heroku addons:create heroku-postgresql:mini
git push heroku main
heroku run python init_db.py
heroku run python seed_data.py
```

### Option 2: Use Railway

Railway is another alternative:

```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy
railway login
railway init
railway up
```

### Option 3: Test Locally First

Before deploying, make sure everything works locally:

```bash
# Backend
cd backend
python run.py

# Frontend (new terminal)
cd frontend
npm run dev
```

Visit http://localhost:5173 and test all features.

---

## 📞 Get Help

If you're still stuck, provide:
1. **Platform**: Render/Heroku/Railway
2. **Error logs**: Copy from deployment logs
3. **What you tried**: List troubleshooting steps

Common issues are usually:
- Missing dependencies in requirements.txt
- Wrong build/start commands
- Database connection issues
- CORS configuration

---

## ✅ Successful Deployment Indicators

You'll know deployment succeeded when:
- ✅ Build completes without errors
- ✅ Service shows "Live" status
- ✅ Backend URL returns JSON (not 404)
- ✅ Frontend loads without errors
- ✅ Can create and join rooms
- ✅ Real-time bidding works

Test your deployment:
```bash
# Test backend
curl https://your-backend-url.onrender.com/api/players

# Should return JSON with player data
```
