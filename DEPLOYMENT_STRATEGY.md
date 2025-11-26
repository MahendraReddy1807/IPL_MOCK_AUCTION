# Deployment Strategy - IPL Mock Auction Arena

## ⚠️ Important: Your App Needs Split Deployment

Your application has **WebSocket** support which requires a **persistent server connection**. This means:

- ❌ **Cannot deploy backend to Vercel** (no WebSocket support)
- ✅ **Can deploy frontend to Vercel** (static site)
- ✅ **Must deploy backend to Render/Heroku/Railway** (WebSocket support)

## 🎯 Recommended Deployment Strategy

### **Backend → Render.com** (Free Tier)
- Supports WebSockets
- Supports Flask-SocketIO
- Free tier available
- Easy PostgreSQL integration

### **Frontend → Vercel** (Free Tier)
- Fast global CDN
- Automatic deployments
- Perfect for React/Vite
- Free tier available

---

## 🚀 Step-by-Step Deployment

### Step 1: Deploy Backend to Render.com

1. **Go to** [render.com](https://render.com)

2. **Sign up/Login** with GitHub

3. **New Web Service**
   - Connect your repository
   - Select: `IPL_MOCK_AUCTION`

4. **Configure Service:**
   ```
   Name: ipl-auction-backend
   Environment: Python 3
   Region: Oregon (or closest to you)
   Branch: main
   Root Directory: (leave empty)
   
   Build Command:
   cd backend && pip install -r requirements.txt && python init_db.py && python seed_data.py
   
   Start Command:
   cd backend && gunicorn -k eventlet -w 1 --bind 0.0.0.0:$PORT run:app
   ```

5. **Add Environment Variables:**
   ```
   FLASK_ENV=production
   SECRET_KEY=your-random-secret-key-here-change-this
   CORS_ORIGINS=*
   ```

6. **Create PostgreSQL Database:**
   - New + → PostgreSQL
   - Name: `ipl-auction-db`
   - Plan: Free
   - Copy the **Internal Database URL**

7. **Add DATABASE_URL to Backend:**
   - Go back to your web service
   - Environment → Add Variable
   - Key: `DATABASE_URL`
   - Value: (paste the Internal Database URL)

8. **Deploy!**
   - Click "Create Web Service"
   - Wait 5-10 minutes
   - Copy your backend URL (e.g., `https://ipl-auction-backend.onrender.com`)

### Step 2: Deploy Frontend to Vercel

1. **Go to** [vercel.com](https://vercel.com)

2. **Sign up/Login** with GitHub

3. **New Project**
   - Import your repository
   - Select: `IPL_MOCK_AUCTION`

4. **Configure Project:**
   ```
   Framework Preset: Vite
   Root Directory: frontend
   Build Command: npm run build
   Output Directory: dist
   Install Command: npm install
   ```

5. **Add Environment Variable:**
   ```
   Name: VITE_API_URL
   Value: https://ipl-auction-backend.onrender.com
   (use your actual backend URL from Step 1)
   ```

6. **Deploy!**
   - Click "Deploy"
   - Wait 2-3 minutes
   - Your frontend will be live!

---

## 🧪 Testing Your Deployment

### Test Backend
```bash
# Should return JSON with player data
curl https://your-backend-url.onrender.com/api/players
```

### Test Frontend
1. Visit your Vercel URL
2. Try creating a room
3. Join with another browser/incognito
4. Test bidding functionality

---

## 🔧 Alternative: All-in-One Deployment

If you want everything on one platform:

### Option A: Render.com Only

**Backend:**
- Follow Step 1 above

**Frontend:**
- New Static Site on Render
- Build Command: `cd frontend && npm install && npm run build`
- Publish Directory: `frontend/dist`
- Environment Variable: `VITE_API_URL=<your-backend-url>`

### Option B: Railway.app

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy
railway init
railway up

# Add PostgreSQL
railway add postgresql

# Set environment variables in Railway dashboard
```

### Option C: Heroku

```bash
# Backend
cd backend
heroku create ipl-auction-backend
heroku addons:create heroku-postgresql:mini
git subtree push --prefix backend heroku main
heroku run python init_db.py
heroku run python seed_data.py

# Frontend - deploy to Netlify or Vercel
```

---

## 📋 Deployment Checklist

### Before Deploying:

- [ ] Backend `requirements.txt` has gunicorn, eventlet, psycopg2-binary
- [ ] `Procfile` exists
- [ ] `render.yaml` exists (for Render)
- [ ] `vercel.json` exists (for Vercel)
- [ ] All code committed and pushed to GitHub
- [ ] Tested locally with `gunicorn -k eventlet -w 1 -b 0.0.0.0:5000 run:app`

### After Deploying:

- [ ] Backend returns JSON at `/api/players`
- [ ] Frontend loads without errors
- [ ] Can create rooms
- [ ] Can join rooms
- [ ] Real-time bidding works
- [ ] WebSocket connection established
- [ ] Results page displays correctly

---

## 🆘 Troubleshooting

### "404 NOT_FOUND" on Vercel
**Cause:** Trying to deploy backend to Vercel
**Solution:** Deploy backend to Render.com instead

### "CORS Error"
**Cause:** Frontend can't connect to backend
**Solution:** 
1. Set `CORS_ORIGINS=*` in backend environment variables
2. Ensure `VITE_API_URL` in frontend points to correct backend URL

### "WebSocket Connection Failed"
**Cause:** Backend not supporting WebSockets
**Solution:** Ensure using `gunicorn -k eventlet` (not just `gunicorn`)

### "Database Connection Error"
**Cause:** DATABASE_URL not set or incorrect
**Solution:** 
1. Create PostgreSQL database on Render
2. Copy Internal Database URL
3. Add as `DATABASE_URL` environment variable

---

## 💰 Cost Breakdown

### Free Tier (Recommended for Testing)
- **Render Backend**: Free (spins down after 15 min inactivity)
- **Render PostgreSQL**: Free (90 days, then $7/month)
- **Vercel Frontend**: Free (unlimited)
- **Total**: $0/month (first 90 days)

### Paid Tier (Production Ready)
- **Render Backend**: $7/month (always on)
- **Render PostgreSQL**: $7/month
- **Vercel Frontend**: Free
- **Total**: $14/month

---

## ✅ Success Indicators

Your deployment is successful when:

1. **Backend Health Check:**
   ```bash
   curl https://your-backend.onrender.com/api/players
   # Returns JSON array of players
   ```

2. **Frontend Loads:**
   - No console errors
   - Can see home page
   - Create room button works

3. **WebSocket Works:**
   - Can join rooms
   - Real-time updates work
   - Bidding is synchronized

4. **End-to-End Test:**
   - Create room
   - Join with 2+ users
   - Complete an auction
   - View results

---

## 📞 Quick Help

**Still getting 404?**
- Make sure you're deploying backend to Render (not Vercel)
- Check build logs for errors
- Verify all environment variables are set

**Need the deployment URLs?**
- Backend: Check Render dashboard
- Frontend: Check Vercel dashboard
- Update `VITE_API_URL` if backend URL changes

**Want to test locally first?**
```bash
# Backend
cd backend
gunicorn -k eventlet -w 1 -b 0.0.0.0:5000 run:app

# Frontend (new terminal)
cd frontend
npm run dev
```

---

## 🎉 Next Steps After Deployment

1. Test all features thoroughly
2. Share the URL with friends
3. Gather feedback
4. Implement additional features from FEATURE_IMPLEMENTATION_PLAN.md
5. Monitor performance and errors

Good luck with your deployment! 🚀
