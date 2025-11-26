# IPL Mock Auction Arena - Streamlit Edition

A unified Streamlit application for simulating IPL player auctions with real-time bidding and AI-powered team analysis.

## 🚀 Quick Start

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   streamlit run app.py
   ```

3. **Open in browser:**
   The app will automatically open at `http://localhost:8501`

## 📦 Deployment

### Streamlit Cloud (Recommended)

1. Push code to GitHub repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Select `app.py` as the main file
5. Deploy!

### Render

1. Create `render.yaml` in project root:
   ```yaml
   services:
     - type: web
       name: ipl-auction
       env: python
       buildCommand: pip install -r requirements.txt
       startCommand: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```

2. Connect repository to Render
3. Deploy

### Heroku

1. Create `Procfile`:
   ```
   web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```

2. Deploy:
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

## 🎮 How to Play

1. **Enter Username** - Start by entering your unique username
2. **Create/Join Room** - Create a new room or join with a 6-character code
3. **Configure Team** - Set team name, upload logo, and choose starting purse
4. **Wait for Players** - Need 5-10 participants to start
5. **Bid on Players** - 30 seconds per player, place bids to build your squad
6. **View Results** - See AI-powered team ratings and playing XI selection

## 🏗️ Architecture

```
streamlit_app/
├── app.py                 # Main entry point
├── config.py              # Configuration
├── models/                # SQLAlchemy models
├── services/              # Business logic
├── pages/                 # UI pages
├── utils/                 # Utilities
└── data/                  # Player data CSV
```

## 🔧 Configuration

Edit `config.py` to customize:
- Timer duration (default: 30 seconds)
- Bid increment (default: 5 Lakhs)
- Room capacity (5-10 players)
- Polling interval (default: 2 seconds)

## 📊 Features

- ✅ Real-time multiplayer bidding
- ✅ 100+ IPL players with stats
- ✅ Automatic playing XI selection
- ✅ AI-powered team ratings
- ✅ Impact player selection
- ✅ Multi-user synchronization
- ✅ Responsive design

## 🐛 Troubleshooting

**Database locked error:**
- The app uses SQLite which has limited concurrency
- For production, consider PostgreSQL

**Players not loading:**
- Ensure `data/players.csv` exists
- Check file permissions

**Sync issues:**
- Refresh the page
- Check polling interval in config

## 📝 License

Educational project for IPL auction simulation.
