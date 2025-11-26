# Quick Fix for 404 Deployment Error

## ✅ What I Fixed

1. **Added missing production dependencies** to `backend/requirements.txt`:
   - `gunicorn==21.2.0` (production server)
   - `eventlet==0.33.3` (WebSocket support)
   - `psycopg2-binary==2.9.9` (PostgreSQL driver)

2. **Created `Procfile`** for Heroku/Render deployment

3. **Created `render.yaml`** for automatic Render.com deployment

4. **Created `backend/build.sh`** for build automation

5. **Created `DEPLOYMENT_TROUBLESHOOTING.md`** for future issues

## 🚀 Next Steps

### Option 1: Redeploy on Render (Recommended)

Your GitHub repo is now updated. On Render:

1. **If using Blueprint:**
   - Render will auto-detect the changes
   - Click "Manual Deploy" → "Clear build cache & deploy"

2. **If using Manual Setup:**
   - Go to your backend service
   - Settings → Build & Deploy
   - Update Build Command: `cd backend && pip install -r requirements.txt`
   - Update Start Command: `cd backend && gunicorn -k eventlet -w 1 --bind 0.0.0.0:$PORT run:app`
   - Click "Manual Deploy"

### Option 2: Fresh Deployment

If still having issues, delete the old service and create new:

1. **Delete old services** on Render

2. **Create new Blueprint deployment:**
   - New + → Blueprint
   - Connect GitHub repo
   - Render will use `render.yaml`
   - Click "Apply"

3. **Wait 10-15 minutes** for complete deployment

### Option 3: Test Locally First

Before redeploying, test locally:

```bash
# Install new dependencies
cd backend
pip install -r requirements.txt

# Test with gunicorn
gunicorn -k eventlet -w 1 -b 0.0.0.0:5000 run:app
```

Visit http://localhost:5000/api/players - should return JSON

## 🔍 Verify Deployment

Once deployed, test these URLs:

```bash
# Backend health check
curl https://your-backend-url.onrender.com/api/players

# Should return JSON with player data
```

## ⚠️ Common Issues After Fix

### Issue: "Still getting 404"
**Solution:** Clear build cache and redeploy

### Issue: "Database connection error"
**Solution:** Ensure DATABASE_URL environment variable is set

### Issue: "CORS error"
**Solution:** Set CORS_ORIGINS=* in environment variables

## 📞 Need More Help?

Check `DEPLOYMENT_TROUBLESHOOTING.md` for detailed solutions.

## ✅ Success Indicators

Deployment is successful when:
- Build completes without errors
- Service shows "Live" status  
- Backend URL returns JSON (not 404)
- No errors in logs
