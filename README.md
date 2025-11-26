# IPL Mock Auction Arena

A real-time multiplayer web application for simulating IPL player auctions with AI-based team analysis and predictions.

## 🎯 Overview

The IPL Mock Auction Arena enables 5-10 users to participate in simulated IPL player auctions with real-time bidding, automatic team analysis, and AI-based predictions for optimal team composition. The application features:

- **Real-time Multiplayer Auctions**: Bid on players with live updates via WebSocket
- **AI Team Analysis**: Automatic playing XI selection and team rating calculation
- **Comprehensive Player Database**: 100+ IPL players with detailed statistics
- **Interactive Results Dashboard**: Visual team comparisons and ratings
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices

## 📁 Project Structure

```
.
├── backend/                    # Flask backend application
│   ├── app/
│   │   ├── __init__.py        # Flask app factory
│   │   ├── models/            # Database models (SQLAlchemy)
│   │   ├── services/          # Business logic services
│   │   │   ├── room_service.py      # Room management
│   │   │   ├── team_service.py      # Team operations
│   │   │   ├── auction_service.py   # Auction engine
│   │   │   ├── ai_service.py        # AI analysis & predictions
│   │   │   └── scraper.py           # Player data scraping
│   │   ├── routes/            # REST API endpoints
│   │   ├── events/            # WebSocket event handlers
│   │   └── utils/             # Utility functions & validation
│   ├── data/                  # Sample data files
│   │   └── players.csv        # Player database
│   ├── tests/                 # Test suite
│   │   ├── test_*_properties.py  # Property-based tests
│   │   └── test_api_integration.py  # Integration tests
│   ├── config.py              # Application configuration
│   ├── run.py                 # Application entry point
│   ├── init_db.py             # Database initialization
│   ├── seed_data.py           # Development data seeding
│   ├── requirements.txt       # Python dependencies
│   └── .env.example           # Environment variables template
│
├── frontend/                   # React frontend application
│   ├── src/
│   │   ├── components/        # Reusable React components
│   │   ├── pages/             # Page components
│   │   │   ├── Home.jsx       # Landing page
│   │   │   ├── Lobby.jsx      # Pre-auction lobby
│   │   │   ├── AuctionRoom.jsx  # Live auction interface
│   │   │   └── Results.jsx    # Results dashboard
│   │   ├── services/          # API and Socket.IO services
│   │   │   ├── api.js         # REST API client
│   │   │   └── socket.js      # WebSocket client
│   │   ├── utils/             # Utility functions
│   │   │   └── errorHandler.js  # Error handling utilities
│   │   ├── App.jsx            # Main App component
│   │   ├── main.jsx           # Application entry point
│   │   └── index.css          # Global styles with Tailwind
│   ├── index.html             # HTML template
│   ├── package.json           # Node dependencies
│   ├── vite.config.js         # Vite configuration
│   ├── tailwind.config.js     # Tailwind CSS configuration
│   └── .env.example           # Environment variables template
│
└── .kiro/specs/               # Feature specifications
    └── ipl-mock-auction-arena/
        ├── requirements.md    # EARS-compliant requirements
        ├── design.md          # System design & architecture
        └── tasks.md           # Implementation task list
```

## 🛠️ Technology Stack

### Backend
- **Flask** - Lightweight web framework
- **Flask-SocketIO** - Real-time bidirectional communication
- **SQLAlchemy** - Python SQL toolkit and ORM
- **SQLite** - Embedded database
- **Flask-CORS** - Cross-origin resource sharing
- **BeautifulSoup4** - HTML parsing for web scraping
- **Requests** - HTTP library
- **Hypothesis** - Property-based testing framework
- **Pytest** - Testing framework

### Frontend
- **React 18** - UI framework
- **Vite** - Next-generation build tool
- **TailwindCSS** - Utility-first CSS framework
- **Socket.IO Client** - WebSocket client library
- **Axios** - Promise-based HTTP client
- **React Router** - Client-side routing

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Node.js 16 or higher
- npm or yarn

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment:**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Unix/MacOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   # Windows
   copy .env.example .env

   # Unix/MacOS
   cp .env.example .env
   ```

5. **Initialize database:**
   ```bash
   python init_db.py
   ```

6. **Seed sample data (optional):**
   ```bash
   python seed_data.py
   ```

7. **Run the application:**
   ```bash
   python run.py
   ```

   The backend will be available at `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Set up environment variables:**
   ```bash
   # Windows
   copy .env.example .env

   # Unix/MacOS
   cp .env.example .env
   ```

4. **Run the development server:**
   ```bash
   npm run dev
   # or
   yarn dev
   ```

   The frontend will be available at `http://localhost:5173`

## 📖 Usage Guide

### Creating an Auction

1. Open the application in your browser
2. Enter your username
3. Click "Create Room"
4. Share the room code with other participants (5-10 players required)

### Joining an Auction

1. Enter your username
2. Enter the room code provided by the host
3. Click "Join Room"

### Configuring Your Team

1. In the lobby, enter your team name
2. Upload a team logo (optional)
3. Set your starting purse (default: 100 Lakhs)
4. Wait for all participants to configure their teams

### During the Auction

1. The host starts the auction when all participants are ready
2. Players are presented one by one with a 30-second timer
3. Click "Place Bid" to increase the current bid
4. The highest bidder when the timer expires wins the player
5. Your purse is automatically updated after each purchase

### Viewing Results

1. After all players are sold, the auction completes automatically
2. View the results dashboard with:
   - Winner announcement
   - Team ratings comparison
   - Full squad for each team
   - Playing XI and impact player selections
   - Detailed team ratings breakdown

## 🔌 API Documentation

### REST API Endpoints

#### Room Management
- `POST /api/rooms/create` - Create a new auction room
  - Body: `{ "host_username": "string" }`
  - Response: `{ "success": true, "room_code": "string", "status": "lobby" }`

- `POST /api/rooms/join` - Join an existing room
  - Body: `{ "room_code": "string", "username": "string" }`
  - Response: `{ "success": true, "room_code": "string", "participants": [] }`

- `GET /api/rooms/{code}` - Get room details
  - Response: `{ "room_code": "string", "status": "string", "participants": [] }`

#### Team Management
- `POST /api/teams/configure` - Configure team details
  - Body: `{ "room_code": "string", "username": "string", "team_name": "string", "purse": number }`
  - Response: `{ "success": true, "team_name": "string", "purse": number }`

- `POST /api/teams/upload-logo` - Upload team logo
  - Body: FormData with `logo` file
  - Response: `{ "success": true, "logo_url": "string" }`

#### Player & Auction
- `GET /api/players` - Get all players
  - Response: `{ "players": [] }`

- `GET /api/auction/{room_code}/state` - Get current auction state
  - Response: `{ "current_player": {}, "current_bid": number, "teams": [] }`

- `GET /api/results/{room_code}` - Get auction results
  - Response: `{ "teams": [], "winner": {} }`

### WebSocket Events

#### Client → Server
- `join_room` - Join a room
  - Data: `{ "room_code": "string", "username": "string" }`

- `place_bid` - Place a bid on current player
  - Data: `{ "room_code": "string", "username": "string" }`

- `start_auction` - Start the auction (host only)
  - Data: `{ "room_code": "string" }`

#### Server → Client
- `user_joined` - User joined the room
  - Data: `{ "username": "string", "participants_count": number }`

- `player_presented` - New player presented for auction
  - Data: `{ "player": {}, "timer_duration": 30 }`

- `bid_placed` - Bid placed successfully
  - Data: `{ "username": "string", "bid_amount": number, "current_highest": "string" }`

- `player_sold` - Player sold to highest bidder
  - Data: `{ "player": {}, "sold_to": "string", "sold_price": number }`

- `purse_updated` - Team purse updated
  - Data: `{ "team_id": number, "new_purse": number }`

- `auction_completed` - Auction finished
  - Data: `{ "message": "string" }`

- `error` - Error occurred
  - Data: `{ "message": "string" }`

## 🧪 Testing

### Running All Tests
```bash
cd backend
pytest
```

### Running Specific Test Suites
```bash
# Property-based tests
pytest tests/test_*_properties.py -v

# Integration tests
pytest tests/test_api_integration.py -v

# Specific test file
pytest tests/test_room_properties.py -v
```

### Test Coverage
```bash
pytest --cov=app --cov-report=html
```

### Property-Based Testing
The application uses Hypothesis for property-based testing to verify correctness properties across many randomly generated inputs. Each property test runs 100 iterations by default.

Example properties tested:
- Room code uniqueness
- Purse validation and deduction
- Playing XI composition constraints
- Team rating calculations
- Results data completeness

## 🌍 Environment Variables

### Backend (.env)
```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///auction.db
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:5000/api
VITE_SOCKET_URL=http://localhost:5000
```

## 🏗️ Development

### Database Management

**Initialize database:**
```bash
python backend/init_db.py
```

**Seed sample data:**
```bash
python backend/seed_data.py
```

**Clear all data:**
```bash
python backend/seed_data.py --clear
```

### Code Style
- Backend: Follow PEP 8 guidelines
- Frontend: Follow Airbnb JavaScript Style Guide
- Use meaningful variable and function names
- Add docstrings/comments for complex logic

### Adding New Features
1. Update requirements in `.kiro/specs/ipl-mock-auction-arena/requirements.md`
2. Design the feature in `design.md`
3. Add implementation tasks to `tasks.md`
4. Implement with tests
5. Update documentation

## 🐛 Troubleshooting

### Backend Issues

**Port already in use:**
```bash
# Change port in run.py or kill the process using port 5000
```

**Database locked:**
```bash
# Close all connections and restart the application
```

**Import errors:**
```bash
# Ensure virtual environment is activated and dependencies are installed
pip install -r requirements.txt
```

### Frontend Issues

**Module not found:**
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**WebSocket connection failed:**
- Ensure backend is running
- Check VITE_SOCKET_URL in .env
- Verify CORS configuration

## 📝 License

This project is for educational purposes.

## 🤝 Contributing

This is an educational project. Feel free to fork and experiment!

## 📧 Support

For issues and questions, please refer to the specification documents in `.kiro/specs/ipl-mock-auction-arena/`.
