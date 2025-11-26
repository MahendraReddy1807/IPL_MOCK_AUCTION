# Deployment Guide - IPL Mock Auction Arena

## 🚀 Quick Deploy

### Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL 12+ or SQLite
- Git

### Local Development Setup

#### 1. Clone Repository
```bash
git clone https://github.com/MahendraReddy1807/IPL_MOCK_AUCTION.git
cd IPL_MOCK_AUCTION
```

#### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run database migrations
python init_db.py

# Run migration for new features
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); with open('migrations/add_all_features.sql') as f: db.engine.execute(f.read())"

# Seed database
python seed_data.py

# Run backend
python run.py
```

#### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

#### 4. Access Application
- Frontend: http://localhost:5173
- Backend API: http://localhost:5000

---

## 🌐 Production Deployment

### Option 1: Deploy to Render.com (Recommended)

#### Backend Deployment
1. Create account on [Render.com](https://render.com)
2. Create new Web Service
3. Connect GitHub repository
4. Configure:
   - **Build Command**: `cd backend && pip install -r requirements.txt`
   - **Start Command**: `cd backend && gunicorn run:app`
   - **Environment**: Python 3
5. Add Environment Variables:
   - `DATABASE_URL`: Your PostgreSQL URL
   - `SECRET_KEY`: Random secret key
   - `FLASK_ENV`: production

#### Frontend Deployment
1. Create new Static Site on Render
2. Configure:
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Publish Directory**: `frontend/dist`
3. Add Environment Variable:
   - `VITE_API_URL`: Your backend URL

### Option 2: Deploy to Heroku

#### Backend
```bash
cd backend
heroku create ipl-auction-backend
heroku addons:create heroku-postgresql:hobby-dev
git push heroku main
heroku run python init_db.py
heroku run python seed_data.py
```

#### Frontend
```bash
cd frontend
# Update VITE_API_URL in .env to Heroku backend URL
npm run build
# Deploy dist folder to Netlify/Vercel
```

### Option 3: Deploy to Railway

1. Install Railway CLI
```bash
npm install -g @railway/cli
```

2. Deploy Backend
```bash
cd backend
railway login
railway init
railway up
```

3. Deploy Frontend
```bash
cd frontend
railway init
railway up
```

---

## 🐳 Docker Deployment

### Using Docker Compose

```bash
# Build and run
docker-compose up --build

# Access
# Frontend: http://localhost:3000
# Backend: http://localhost:5000
```

---

## 📦 Environment Variables

### Backend (.env)
```env
FLASK_APP=run.py
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:password@localhost/auction_db
CORS_ORIGINS=https://your-frontend-url.com

# Optional: Email/SMS (for future features)
SENDGRID_API_KEY=your-key
TWILIO_ACCOUNT_SID=your-sid
TWILIO_AUTH_TOKEN=your-token
```

### Frontend (.env)
```env
VITE_API_URL=https://your-backend-url.com
VITE_WS_URL=wss://your-backend-url.com
```

---

## 🔧 Database Migration

### Run New Features Migration
```bash
cd backend
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); exec(open('migrations/add_all_features.sql').read())"
```

### Verify Migration
```bash
python -c "from app import create_app, db; from app.models.user import User; from app.models.achievement import Achievement; app = create_app(); app.app_context().push(); print('Users table:', User.query.count()); print('Achievements:', Achievement.query.count())"
```

---

## 🚦 Health Checks

### Backend Health
```bash
curl http://localhost:5000/api/health
```

### Database Connection
```bash
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.engine.execute('SELECT 1'); print('Database connected!')"
```

---

## 📊 Monitoring

### Logs
```bash
# Backend logs
tail -f backend/logs/app.log

# Frontend logs (in browser console)
```

### Performance
- Use browser DevTools for frontend performance
- Monitor backend with Flask-Profiler (optional)

---

## 🔒 Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Use HTTPS in production
- [ ] Enable CORS only for your frontend domain
- [ ] Use environment variables for sensitive data
- [ ] Enable rate limiting
- [ ] Regular security updates

---

## 🆘 Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
psql -U postgres -c "SELECT version();"

# Reset database
python init_db.py --reset
```

### Port Already in Use
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:5000 | xargs kill -9
```

### Module Not Found
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

---

## 📝 Post-Deployment

1. Test all core features
2. Seed database with real player data
3. Create admin user
4. Configure email/SMS (optional)
5. Set up monitoring
6. Enable backups

---

## 🔄 Updates & Maintenance

### Pull Latest Changes
```bash
git pull origin main
cd backend && pip install -r requirements.txt
cd frontend && npm install
```

### Database Backup
```bash
# PostgreSQL
pg_dump auction_db > backup_$(date +%Y%m%d).sql

# SQLite
cp backend/auction.db backend/backup_$(date +%Y%m%d).db
```

---

## 📞 Support

For issues or questions:
- GitHub Issues: https://github.com/MahendraReddy1807/IPL_MOCK_AUCTION/issues
- Documentation: See README.md

---

## 🎯 Feature Rollout Plan

### Phase 1 (Current) - Core Features ✅
- Basic auction functionality
- Real-time bidding
- Team management
- AI opponents
- Database foundation for 23 new features

### Phase 2 (Next) - Enhanced Features
- User authentication
- RTM cards
- Team strength meter
- Player comparison
- Dark/light theme

### Phase 3 - Advanced Features
- Tournament mode
- Trade system
- Achievement system
- Analytics dashboard

### Phase 4 - Social Features
- Spectator mode
- Team alliances
- Notifications
- Email integration

---

## 📈 Scaling Considerations

### For High Traffic
- Use Redis for caching
- Enable CDN for frontend
- Use connection pooling for database
- Consider load balancer
- Implement rate limiting

### Database Optimization
- Regular VACUUM (PostgreSQL)
- Index optimization
- Query performance monitoring
- Connection pool tuning
