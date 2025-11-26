# Design Document

## Overview

This document outlines the technical design for converting the IPL Mock Auction Arena from a Flask backend + React frontend architecture to a unified Streamlit application. The conversion maintains all core auction functionality while simplifying the architecture by eliminating the need for separate frontend/backend codebases and WebSocket infrastructure.

The Streamlit application will leverage:
- **Session State** for user-specific data persistence
- **Database polling** for multi-user synchronization
- **Auto-refresh** for real-time updates
- **Native widgets** for UI components
- **SQLAlchemy models** preserved from the original application

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Application                     │
│                                                              │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐           │
│  │   Home     │  │   Lobby    │  │  Auction   │           │
│  │   Page     │  │   Page     │  │   Page     │           │
│  └────────────┘  └────────────┘  └────────────┘           │
│                                                              │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐           │
│  │  Results   │  │  Services  │  │   Utils    │           │
│  │   Page     │  │   Layer    │  │            │           │
│  └────────────┘  └────────────┘  └────────────┘           │
│                                                              │
│  ┌──────────────────────────────────────────────┐          │
│  │         SQLAlchemy ORM + SQLite DB           │          │
│  └──────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

### Application Structure

```
streamlit_app/
├── app.py                      # Main Streamlit application entry point
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── .streamlit/
│   └── config.toml            # Streamlit configuration
├── models/                     # SQLAlchemy models (preserved from backend)
│   ├── __init__.py
│   ├── room.py
│   ├── team.py
│   ├── player.py
│   ├── auction_player.py
│   ├── team_player.py
│   ├── team_rating.py
│   └── simple_user.py
├── services/                   # Business logic layer
│   ├── __init__.py
│   ├── room_service.py
│   ├── team_service.py
│   ├── auction_service.py
│   ├── ai_service.py
│   └── data_service.py
├── pages/                      # Streamlit page modules
│   ├── __init__.py
│   ├── home.py
│   ├── lobby.py
│   ├── auction.py
│   └── results.py
├── utils/                      # Utility functions
│   ├── __init__.py
│   ├── validation.py
│   ├── db_utils.py
│   └── timer.py
└── data/
    └── players.csv            # Player database CSV
```

## Components and Interfaces

### 1. Main Application (app.py)

The main entry point that handles:
- Database initialization
- Session state initialization
- Page routing via sidebar navigation
- Global configuration

**Key Functions:**
- `init_database()` - Initialize SQLite database and load player data
- `init_session_state()` - Initialize Streamlit session state variables
- `render_navigation()` - Render sidebar navigation
- `main()` - Main application loop

### 2. Page Modules

#### Home Page (`pages/home.py`)
- Username input
- Create room button
- Join room input and button
- Room code display after creation

**Session State Variables:**
- `username` - Current user's username
- `room_code` - Current room code
- `is_host` - Boolean indicating if user is host
- `page` - Current page name

#### Lobby Page (`pages/lobby.py`)
- Display room code and participants
- Team configuration form (name, logo upload, purse)
- Start auction button (host only)
- Real-time participant list updates

**Session State Variables:**
- `team_configured` - Boolean indicating team setup completion
- `team_name` - User's team name
- `team_logo` - Uploaded logo file
- `initial_purse` - Starting purse amount

#### Auction Page (`pages/auction.py`)
- Current player display with details
- Bid button
- Current bid and highest bidder display
- Timer countdown
- Team purse display
- Player queue/progress indicator

**Session State Variables:**
- `current_player_id` - ID of player being auctioned
- `current_bid` - Current highest bid
- `highest_bidder` - Username of highest bidder
- `timer_start` - Timestamp when timer started
- `my_purse` - Current user's remaining purse

#### Results Page (`pages/results.py`)
- Winner announcement
- Team ratings comparison (bar chart)
- All teams display with:
  - Team name and logo
  - Total rating
  - Playing XI
  - Impact player
  - Bench players
  - Rating breakdown (batting, bowling, balance)

### 3. Service Layer

All service modules are preserved from the original backend with minimal modifications:

#### room_service.py
- `generate_room_code()` - Generate unique 6-character room code
- `create_room(host_username)` - Create new auction room
- `join_room(room_code, username)` - Add user to existing room
- `get_room_participants(room_code)` - Get list of participants
- `start_auction(room_code, host_username)` - Transition room to active status

#### team_service.py
- `configure_team(room_code, username, team_name, purse, logo_path)` - Set up team
- `get_team(room_code, username)` - Retrieve team details
- `update_purse(team_id, new_purse)` - Update team's remaining purse
- `get_all_teams(room_code)` - Get all teams in a room

#### auction_service.py
- `initialize_auction(room_code)` - Create AuctionPlayer records
- `present_next_player(room_code)` - Get next unsold player
- `place_bid(room_code, username)` - Process bid attempt
- `handle_timer_expiry(room_code)` - Assign player to highest bidder
- `get_current_auction_state(room_code)` - Get current auction status

#### ai_service.py
- `select_playing_xi(team_id)` - Choose optimal 11 players
- `select_impact_player(team_id)` - Choose best bench player
- `calculate_team_rating(team_id)` - Compute comprehensive rating
- `determine_winner(room_code)` - Find team with highest rating

#### data_service.py (new)
- `load_players_from_csv()` - Import players from CSV file
- `seed_database()` - Initialize database with player data
- `get_all_players()` - Retrieve all players

### 4. Utility Modules

#### validation.py
- `validate_username(username)` - Check username format
- `validate_team_name(team_name)` - Check team name format
- `validate_purse(purse)` - Check purse amount is valid
- `validate_room_code(room_code)` - Check room code format

#### db_utils.py
- `get_db_session()` - Get SQLAlchemy session
- `init_db()` - Initialize database schema
- `retry_on_lock(func, max_retries=3)` - Retry database operations on lock

#### timer.py
- `get_remaining_time(start_time, duration)` - Calculate time left
- `is_timer_expired(start_time, duration)` - Check if timer expired

## Data Models

All SQLAlchemy models are preserved from the original backend application:

### Room
- `id` (Integer, PK)
- `code` (String, unique)
- `status` (String: 'lobby', 'active', 'completed')
- `min_users` (Integer, default 5)
- `max_users` (Integer, default 10)
- `host_username` (String)
- `created_at` (DateTime)

### Team
- `id` (Integer, PK)
- `room_id` (Integer, FK)
- `username` (String)
- `team_name` (String)
- `logo_url` (String, nullable)
- `initial_purse` (Float)
- `purse_left` (Float)
- `created_at` (DateTime)

### Player
- `id` (Integer, PK)
- `name` (String)
- `role` (String: 'BAT', 'BOWL', 'AR', 'WK')
- `is_overseas` (Boolean)
- `base_price` (Float)
- `batting_score` (Float)
- `bowling_score` (Float)
- `overall_score` (Float)

### AuctionPlayer
- `id` (Integer, PK)
- `room_id` (Integer, FK)
- `player_id` (Integer, FK)
- `is_sold` (Boolean)
- `sold_price` (Float, nullable)
- `sold_to_team_id` (Integer, FK, nullable)
- `sold_at` (DateTime, nullable)

### TeamPlayer
- `id` (Integer, PK)
- `team_id` (Integer, FK)
- `player_id` (Integer, FK)
- `price` (Float)
- `in_playing_xi` (Boolean)
- `is_impact_player` (Boolean)

### TeamRating
- `id` (Integer, PK)
- `team_id` (Integer, FK)
- `overall_rating` (Float)
- `batting_rating` (Float)
- `bowling_rating` (Float)
- `balance_score` (Float)
- `bench_depth` (Float)
- `role_coverage` (Float)

### User (SimpleUser)
- `id` (Integer, PK)
- `username` (String)
- `room_id` (Integer, FK)
- `created_at` (DateTime)



## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Room code uniqueness
*For any* two rooms created by the system, their room codes should be different
**Validates: Requirements 1.2, 4.2**

### Property 2: Session state persistence across page navigation
*For any* user navigating between pages, their username and room_code in session state should remain unchanged
**Validates: Requirements 3.2**

### Property 3: Team name uniqueness within room
*For any* room, no two teams should have the same team_name
**Validates: Requirements 5.3**

### Property 4: Purse deduction correctness
*For any* successful bid, the team's purse_left should decrease by exactly the bid amount
**Validates: Requirements 7.5**

### Property 5: Sufficient purse validation
*For any* bid attempt, if the new bid amount exceeds the team's purse_left, the bid should be rejected
**Validates: Requirements 7.3**

### Property 6: Playing XI composition constraints
*For any* selected playing XI, it should contain exactly 1 WK, at least 3 BAT, at least 2 BOWL, between 1-3 AR, and at most 4 overseas players
**Validates: Requirements 12.2**

### Property 7: Timer expiry player assignment
*For any* player auction where the timer expires, the player should be assigned to the highest bidder if one exists
**Validates: Requirements 7.5, 8.4**

### Property 8: Auction completion detection
*For any* room, when all players in the player pool are marked as sold, the auction should be marked as complete
**Validates: Requirements 8.5**

### Property 9: Winner determination correctness
*For any* completed auction, the winning team should be the team with the highest overall_rating
**Validates: Requirements 9.3**

### Property 10: Database state consistency after refresh
*For any* user refreshing their page, the displayed auction state should match the current database state
**Validates: Requirements 10.1, 10.3**

## Error Handling

### Database Errors

**SQLite Lock Handling:**
- Implement retry logic with exponential backoff (3 attempts)
- Display user-friendly message: "Database is busy, please wait..."
- Log detailed error for debugging

**Connection Errors:**
- Attempt to reconnect to database
- Display error message with option to refresh page
- Fallback to read-only mode if writes fail

### Validation Errors

**Input Validation:**
- Display inline error messages using `st.error()`
- Prevent form submission until validation passes
- Provide clear guidance on valid input format

**Business Logic Validation:**
- Check room capacity before allowing join
- Verify sufficient purse before accepting bid
- Validate team configuration completeness before auction start

### Session State Errors

**Missing Session Variables:**
- Redirect to home page if critical variables missing
- Display warning message explaining the redirect
- Initialize default values for optional variables

**Stale Session Data:**
- Implement periodic session state refresh from database
- Clear session state on explicit logout/exit
- Handle concurrent session conflicts gracefully

### Timer Synchronization Errors

**Clock Drift:**
- Use server-side timestamps stored in database
- Calculate remaining time based on database timestamp
- Refresh timer display every second

**Missed Timer Expiry:**
- Check for expired timers on every page load
- Process any pending timer expiries before rendering
- Log timer expiry events for audit trail

## Testing Strategy

### Unit Testing

Unit tests will verify specific examples and edge cases:

**Room Service Tests:**
- Test room creation with valid host username
- Test joining non-existent room returns error
- Test joining full room returns error
- Test room code generation produces 6-character codes

**Team Service Tests:**
- Test team configuration with valid inputs
- Test duplicate team name rejection
- Test purse update with valid amount
- Test logo upload and storage

**Auction Service Tests:**
- Test bid placement with sufficient purse
- Test bid rejection with insufficient purse
- Test player assignment on timer expiry
- Test auction completion detection

**AI Service Tests:**
- Test playing XI selection with valid squad
- Test playing XI selection with insufficient players
- Test impact player selection from bench
- Test team rating calculation

### Property-Based Testing

Property-based tests will verify universal properties across many randomly generated inputs using the **Hypothesis** library (Python's standard PBT framework). Each property test will run a minimum of 100 iterations.

**Property Test 1: Room code uniqueness**
- **Feature: streamlit-conversion, Property 1: Room code uniqueness**
- Generate multiple room creation requests
- Verify all generated room codes are unique
- **Validates: Requirements 1.2, 4.2**

**Property Test 2: Session state persistence**
- **Feature: streamlit-conversion, Property 2: Session state persistence across page navigation**
- Simulate page navigation with random session state
- Verify username and room_code remain unchanged
- **Validates: Requirements 3.2**

**Property Test 3: Team name uniqueness**
- **Feature: streamlit-conversion, Property 3: Team name uniqueness within room**
- Generate random team configurations for same room
- Verify duplicate team names are rejected
- **Validates: Requirements 5.3**

**Property Test 4: Purse deduction**
- **Feature: streamlit-conversion, Property 4: Purse deduction correctness**
- Generate random successful bids
- Verify purse decreases by exact bid amount
- **Validates: Requirements 7.5**

**Property Test 5: Purse validation**
- **Feature: streamlit-conversion, Property 5: Sufficient purse validation**
- Generate random bids exceeding purse
- Verify all such bids are rejected
- **Validates: Requirements 7.3**

**Property Test 6: Playing XI constraints**
- **Feature: streamlit-conversion, Property 6: Playing XI composition constraints**
- Generate random player squads
- Verify selected XI meets all role constraints
- **Validates: Requirements 12.2**

**Property Test 7: Timer expiry assignment**
- **Feature: streamlit-conversion, Property 7: Timer expiry player assignment**
- Generate random auction states with expired timers
- Verify player assigned to highest bidder
- **Validates: Requirements 7.5, 8.4**

**Property Test 8: Auction completion**
- **Feature: streamlit-conversion, Property 8: Auction completion detection**
- Generate random auction states with all players sold
- Verify auction marked as complete
- **Validates: Requirements 8.5**

**Property Test 9: Winner determination**
- **Feature: streamlit-conversion, Property 9: Winner determination correctness**
- Generate random completed auctions with team ratings
- Verify winner has highest rating
- **Validates: Requirements 9.3**

**Property Test 10: Database consistency**
- **Feature: streamlit-conversion, Property 10: Database state consistency after refresh**
- Generate random auction states in database
- Simulate page refresh and verify displayed state matches
- **Validates: Requirements 10.1, 10.3**

### Integration Testing

Integration tests will verify end-to-end workflows:

**Complete Auction Flow:**
1. Create room
2. Multiple users join
3. Configure teams
4. Start auction
5. Place bids
6. Complete auction
7. View results

**Multi-User Synchronization:**
1. Multiple users in same room
2. One user places bid
3. Verify all users see updated state
4. Verify database reflects changes

**Error Recovery:**
1. Simulate database lock
2. Verify retry mechanism works
3. Verify user sees appropriate message
4. Verify operation completes successfully

## Multi-User Synchronization

### Approach

Since Streamlit doesn't have built-in WebSocket support like Flask-SocketIO, we'll use a **database polling** approach with **auto-refresh**:

1. **Database as Source of Truth**: All state changes are immediately written to SQLite database
2. **Periodic Polling**: Each user's page polls the database every 2-3 seconds
3. **Auto-Refresh**: Use `st.rerun()` to refresh the page when changes detected
4. **Optimistic Updates**: Show user's own actions immediately, then confirm with database

### Implementation Details

**Polling Mechanism:**
```python
# In auction page
if 'last_poll' not in st.session_state:
    st.session_state.last_poll = time.time()

current_time = time.time()
if current_time - st.session_state.last_poll > 2:  # Poll every 2 seconds
    # Check database for changes
    current_state = get_current_auction_state(st.session_state.room_code)
    
    # If state changed, update session and rerun
    if state_has_changed(current_state):
        update_session_state(current_state)
        st.rerun()
    
    st.session_state.last_poll = current_time
```

**State Change Detection:**
- Compare current player ID with session state
- Compare current bid with session state
- Compare highest bidder with session state
- Compare timer status with session state

**Conflict Resolution:**
- Last write wins for bid placement
- Database timestamp determines order
- Display conflict messages to users if needed

### Timer Synchronization

**Server-Side Timer:**
- Store timer start timestamp in database
- Calculate remaining time on each poll
- All users calculate from same timestamp
- Auto-advance when timer expires

**Timer Display:**
```python
# Calculate remaining time
start_time = get_timer_start_from_db(room_code)
elapsed = time.time() - start_time
remaining = max(0, 30 - elapsed)

# Display countdown
st.metric("Time Remaining", f"{int(remaining)}s")

# Check for expiry
if remaining == 0 and not timer_processed:
    handle_timer_expiry(room_code)
    present_next_player(room_code)
    st.rerun()
```

## Deployment

### Streamlit Cloud Deployment

**Prerequisites:**
- GitHub repository with code
- Streamlit Cloud account (free tier available)

**Configuration Files:**

**requirements.txt:**
```
streamlit>=1.28.0
sqlalchemy>=2.0.0
pandas>=2.0.0
pillow>=10.0.0
hypothesis>=6.90.0
pytest>=7.4.0
```

**.streamlit/config.toml:**
```toml
[server]
headless = true
port = 8501
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#FF6B35"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
```

**Deployment Steps:**
1. Push code to GitHub repository
2. Connect repository to Streamlit Cloud
3. Select main branch and app.py as entry point
4. Configure secrets (if any) in Streamlit Cloud dashboard
5. Deploy and get public URL

### Alternative: Render Deployment

**render.yaml:**
```yaml
services:
  - type: web
    name: ipl-auction-streamlit
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
```

### Alternative: Heroku Deployment

**Procfile:**
```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

**runtime.txt:**
```
python-3.11.0
```

### Database Persistence

**Development:**
- Use local SQLite file
- File persists across runs

**Production (Streamlit Cloud):**
- SQLite file stored in app's file system
- Data persists during session
- Consider using external database (PostgreSQL) for production

**Production (Render/Heroku):**
- Use PostgreSQL addon
- Update SQLAlchemy connection string
- Migrate schema using Alembic

### Environment Variables

**Streamlit Secrets:**
```toml
# .streamlit/secrets.toml
[database]
url = "sqlite:///auction.db"

[app]
secret_key = "your-secret-key-here"
debug = false
```

**Access in Code:**
```python
import streamlit as st

db_url = st.secrets["database"]["url"]
secret_key = st.secrets["app"]["secret_key"]
```

## Performance Considerations

### Database Optimization

**Indexing:**
- Add index on `room.code` for fast lookups
- Add index on `team.room_id` for team queries
- Add index on `auction_player.room_id` and `is_sold` for auction queries

**Query Optimization:**
- Use eager loading for relationships
- Batch database operations where possible
- Cache frequently accessed data in session state

### Streamlit Optimization

**Caching:**
```python
@st.cache_data(ttl=60)
def get_all_players():
    return Player.query.all()

@st.cache_resource
def get_db_connection():
    return create_engine(DATABASE_URL)
```

**Minimize Reruns:**
- Use `st.session_state` to avoid redundant computations
- Only call `st.rerun()` when necessary
- Batch state updates before rerun

### Scalability Limits

**Current Design:**
- Suitable for 5-10 concurrent rooms
- Each room with 5-10 users
- Total: 50-100 concurrent users

**Bottlenecks:**
- SQLite write concurrency
- Polling frequency
- Streamlit server capacity

**Future Improvements:**
- Migrate to PostgreSQL for better concurrency
- Implement WebSocket via custom component
- Use Redis for session state
- Deploy multiple Streamlit instances with load balancer

## Migration Strategy

### Phase 1: Setup
1. Create new `streamlit_app/` directory
2. Copy models from `backend/app/models/` to `streamlit_app/models/`
3. Copy services from `backend/app/services/` to `streamlit_app/services/`
4. Copy `players.csv` to `streamlit_app/data/`

### Phase 2: Core Application
1. Create `app.py` with database initialization
2. Implement session state management
3. Create navigation sidebar
4. Set up configuration files

### Phase 3: Pages
1. Implement Home page
2. Implement Lobby page
3. Implement Auction page
4. Implement Results page

### Phase 4: Testing
1. Write unit tests for services
2. Write property-based tests
3. Perform integration testing
4. Test multi-user scenarios

### Phase 5: Deployment
1. Test locally
2. Deploy to Streamlit Cloud
3. Verify functionality
4. Share public URL

### Phase 6: Cleanup
1. Archive old Flask backend
2. Archive old React frontend
3. Update README
4. Update documentation
