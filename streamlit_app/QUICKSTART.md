# Quick Start Guide

## 🚀 Get Started in 3 Minutes

### Step 1: Install Dependencies (1 minute)

```bash
cd streamlit_app
pip install -r requirements.txt
```

### Step 2: Verify Setup (30 seconds)

```bash
python test_setup.py
```

You should see:
```
✅ ALL TESTS PASSED! Ready to run!
```

### Step 3: Run the App (30 seconds)

```bash
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`

## 🎮 How to Use

### Create Your First Auction

1. **Enter Username**: Type your name (e.g., "John")
2. **Create Room**: Click "Create Room" button
3. **Share Code**: Copy the 6-character room code (e.g., "ABC123")
4. **Configure Team**: 
   - Enter team name (e.g., "Mumbai Indians")
   - Set starting purse (default: 100 Lakhs)
   - Upload logo (optional)
   - Click "Save Team Configuration"

### Join as Another Player

1. Open a new browser window/tab (or incognito mode)
2. Go to `http://localhost:8501`
3. Enter different username (e.g., "Jane")
4. Click "Join Room"
5. Enter the room code
6. Configure your team

### Start the Auction

1. Wait for 5-10 players to join and configure teams
2. As host, click "Start Auction" in the lobby
3. Players will be presented one by one
4. Click "Place Bid" to bid on players
5. Highest bidder when timer expires wins the player

### View Results

1. After all players are sold, results appear automatically
2. See winner announcement
3. View team ratings comparison
4. Check your playing XI and squad

## 🧪 Run Tests (Optional)

```bash
# Run all tests
python run_tests.py

# Or use pytest directly
pytest tests/ -v

# Run specific test file
pytest tests/test_room_service.py -v

# Run property-based tests only
pytest tests/test_properties.py -v
```

## 🌐 Deploy to Cloud

### Streamlit Cloud (Easiest)

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app"
4. Select your repository
5. Set main file: `streamlit_app/app.py`
6. Click "Deploy"
7. Done! Your app is live

### Local Network Access

To allow others on your network to access:

```bash
streamlit run app.py --server.address=0.0.0.0
```

Then share your local IP address (e.g., `http://192.168.1.100:8501`)

## 🐛 Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### Database errors
```bash
# Delete the database and restart
rm auction.db
streamlit run app.py
```

### Port already in use
```bash
# Use different port
streamlit run app.py --server.port=8502
```

### Players not loading
```bash
# Verify CSV file exists
ls data/players.csv

# If missing, copy from backend
cp ../backend/data/players.csv data/
```

## 📚 Learn More

- **Full Documentation**: See `README.md`
- **Deployment Guide**: See `DEPLOYMENT_GUIDE.md`
- **Completion Summary**: See `COMPLETION_SUMMARY.md`
- **Test Examples**: Check `tests/` directory

## 🎯 Key Features

- ✅ Real-time multiplayer bidding
- ✅ 100+ IPL players with stats
- ✅ Automatic playing XI selection
- ✅ AI-powered team ratings
- ✅ 30-second timer per player
- ✅ Multi-user synchronization
- ✅ Responsive design

## 💡 Tips

1. **Test with Multiple Windows**: Open multiple browser windows to simulate multiple users
2. **Use Incognito Mode**: For testing different users on same computer
3. **Check Console**: If issues occur, check terminal for error messages
4. **Refresh Page**: If sync issues, refresh the browser
5. **Clear Cache**: Use Streamlit's "Clear cache" option if needed

## 🎉 You're Ready!

Start your first auction and enjoy the IPL Mock Auction Arena experience!

---

**Need Help?** Check the documentation files or run `python test_setup.py` to verify your setup.
