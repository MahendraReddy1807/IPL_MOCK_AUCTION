# Design Document: IPL Mock Auction Arena

## Overview

The IPL Mock Auction Arena is a real-time multiplayer web application built using Flask (backend), Flask-SocketIO (WebSocket communication), SQLAlchemy (ORM), SQLite (database), and React with TailwindCSS (frontend). The system enables 5-10 users to participate in simulated IPL player auctions, with real-time bidding, automatic team analysis, and AI-based predictions for optimal team composition.

The application follows a client-server architecture with WebSocket-based real-time communication for auction events. The backend handles business logic, data persistence, and auction orchestration, while the frontend provides an interactive UI for users to create rooms, join auctions, place bids, and view results.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend Layer                        │
│  (React + TailwindCSS + Socket.IO Client)                   │
│  - Home Page  - Lobby  - Auction Room  - Results Dashboard  │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/WebSocket
┌────────────────────────┴────────────────────────────────────┐
│                      Backend Layer (Flask)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   REST API   │  │  SocketIO    │  │   Business   │     │
│  │  Endpoints   │  │   Handlers   │  │    Logic     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                    Data Layer (SQLAlchemy)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Models     │  │  Repositories│  │   SQLite DB  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                   External Services Layer                    │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │ Web Scraper  │  │  AI/ML       │                        │
│  │ (BeautifulSoup)│ │  Engine      │                        │
│  └──────────────┘  └──────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

**Backend:**
- Flask: Web framework
- Flask-SocketIO: Real-time bidirectional communication
- SQLAlchemy: ORM for database operations
- SQLite: Lightweight database
- Flask-CORS: Cross-origin resource sharing

**Frontend:**
- React: UI framework
- TailwindCSS: Utility-first CSS framework
- Socket.IO Client: WebSocket client library
- Axios: HTTP client for REST API calls
- React Router: Client-side routing

**Data Collection:**
- Requests: HTTP library for web scraping
- BeautifulSoup4: HTML parsing library
- Pandas: Data manipulation and CSV handling

**AI/ML:**
- Python: Core logic implementation
- Rule-based algorithms: Team selection and rating

### Component Architecture

The system is organized into the following major components:

1. **Room Management Service**: Handles room creation, joining, and participant management
2. **Auction Engine**: Orchestrates the bidding process, timer management, and player assignment
3. **Team Service**: Manages team configuration, purse tracking, and squad composition
4. **Player Service**: Handles player data, scraping, and overall score calculation
5. **AI Analysis Service**: Implements playing XI selection, impact player selection, and team rating
6. **WebSocket Manager**: Manages real-time event broadcasting to connected clients
7. **Frontend Components**: React components for each page and UI element

## Components and Interfaces

### Backend Components

#### 1. Room Management Service

**Responsibilities:**
- Generate unique room codes
- Create and manage auction rooms
- Track room participants
- Validate room capacity constraints
- Manage room state transitions (lobby → active → completed)

**Key Methods:**
```python
create_room(host_username: str) -> Room
join_room(room_code: str, username: str) -> bool
get_room_participants(room_code: str) -> List[User]
start_auction(room_code: str, host_username: str) -> bool
```

#### 2. Auction Engine

**Responsibilities:**
- Manage auction flow (player presentation, bidding, assignment)
- Handle countdown timer for each player
- Validate bids against purse constraints
- Assign players to winning teams
- Track auction progress

**Key Methods:**
```python
present_next_player(room_code: str) -> Player
place_bid(room_code: str, username: str, bid_amount: float) -> BidResult
handle_timer_expiry(room_code: str) -> SoldPlayer
get_current_auction_state(room_code: str) -> AuctionState
```

#### 3. Team Service

**Responsibilities:**
- Store team configuration (name, logo, purse)
- Update purse after player purchases
- Track squad composition
- Retrieve team players

**Key Methods:**
```python
configure_team(username: str, team_name: str, logo_url: str, purse: float) -> Team
update_purse(team_id: int, amount: float) -> Team
add_player_to_team(team_id: int, player_id: int, price: float) -> TeamPlayer
get_team_squad(team_id: int) -> List[Player]
```

#### 4. Player Service

**Responsibilities:**
- Execute web scraping to collect player data
- Parse and clean player statistics
- Calculate overall player scores
- Import player data into database
- Provide player information for auction

**Key Methods:**
```python
scrape_player_data() -> DataFrame
calculate_overall_score(batting_score: float, bowling_score: float, role: str) -> float
import_players_to_db(csv_path: str) -> int
get_available_players(room_code: str) -> List[Player]
```

#### 5. AI Analysis Service

**Responsibilities:**
- Select optimal playing XI based on constraints
- Choose impact player from bench
- Calculate team ratings (batting, bowling, balance, bench depth)
- Determine winning team

**Key Methods:**
```python
select_playing_xi(team_id: int) -> List[Player]
select_impact_player(team_id: int) -> Player
calculate_team_rating(team_id: int) -> TeamRating
determine_winner(room_code: str) -> Team
```

#### 6. WebSocket Manager

**Responsibilities:**
- Manage Socket.IO connections
- Broadcast events to room participants
- Handle client disconnections

**Key Events:**
```python
# Server emits
'user_joined' -> {username, participants_count}
'auction_started' -> {room_code}
'player_presented' -> {player_data, timer_duration}
'bid_placed' -> {username, bid_amount, current_highest}
'player_sold' -> {player, sold_to, sold_price}
'purse_updated' -> {team_id, new_purse}
'auction_completed' -> {results_url}

# Client emits
'join_room' -> {room_code, username}
'place_bid' -> {room_code, username}
'start_auction' -> {room_code}
```

### Frontend Components

#### 1. Home Page Component
- Create room button
- Join room input and button
- Navigation to lobby

#### 2. Lobby Component
- Display room code
- List of joined participants
- Team configuration form (name, logo upload, purse)
- Start auction button (host only)

#### 3. Auction Room Component
- Current player card (name, role, stats, rating)
- Countdown timer
- Bid button
- Bid history panel
- Teams sidebar (purse, squad size)

#### 4. Results Dashboard Component
- Team cards with logo and name
- Full squad display
- Playing XI highlight
- Impact player indicator
- Team rating visualization
- Winner announcement

### REST API Endpoints

```
POST   /api/rooms/create          - Create a new auction room
POST   /api/rooms/join             - Join an existing room
GET    /api/rooms/{code}           - Get room details
POST   /api/teams/configure        - Configure team details
POST   /api/teams/upload-logo      - Upload team logo
GET    /api/players                - Get all players
GET    /api/auction/{room_code}/state - Get current auction state
GET    /api/results/{room_code}    - Get auction results
```

## Data Models

### Database Schema

#### Users Table
```python
class User(db.Model):
    id: Integer (PK)
    username: String(100)
    room_id: Integer (FK -> rooms.id)
    created_at: DateTime
```

#### Rooms Table
```python
class Room(db.Model):
    id: Integer (PK)
    code: String(20) (Unique)
    status: Enum('lobby', 'active', 'completed')
    min_users: Integer (default=5)
    max_users: Integer (default=10)
    host_username: String(100)
    created_at: DateTime
```

#### Teams Table
```python
class Team(db.Model):
    id: Integer (PK)
    room_id: Integer (FK -> rooms.id)
    username: String(100)
    team_name: String(100)
    logo_url: String(255)
    initial_purse: Float
    purse_left: Float
    created_at: DateTime
```

#### Players Table
```python
class Player(db.Model):
    id: Integer (PK)
    name: String(100)
    role: Enum('BAT', 'BOWL', 'AR', 'WK')
    country: String(50)
    base_price: Float
    batting_score: Float
    bowling_score: Float
    overall_score: Float
    is_overseas: Boolean
```

#### AuctionPlayers Table
```python
class AuctionPlayer(db.Model):
    id: Integer (PK)
    room_id: Integer (FK -> rooms.id)
    player_id: Integer (FK -> players.id)
    is_sold: Boolean
    sold_price: Float (nullable)
    sold_to_team_id: Integer (FK -> teams.id, nullable)
    sold_at: DateTime (nullable)
```

#### TeamPlayers Table
```python
class TeamPlayer(db.Model):
    id: Integer (PK)
    team_id: Integer (FK -> teams.id)
    player_id: Integer (FK -> players.id)
    price: Float
    in_playing_xi: Boolean (default=False)
    is_impact_player: Boolean (default=False)
    added_at: DateTime
```

#### TeamRatings Table
```python
class TeamRating(db.Model):
    id: Integer (PK)
    team_id: Integer (FK -> teams.id)
    overall_rating: Float
    batting_rating: Float
    bowling_rating: Float
    balance_score: Float
    bench_depth: Float
    role_coverage: Float
    calculated_at: DateTime
```

### Data Flow

1. **Room Creation Flow:**
   - User submits create room request → Backend generates unique code → Room record created → Code returned to user

2. **Joining Flow:**
   - User enters room code → Backend validates room exists and has capacity → User added to room → WebSocket broadcasts update

3. **Auction Flow:**
   - Host starts auction → Room status changes to 'active' → First player presented → Timer starts → Users place bids → Timer expires → Player assigned to highest bidder → Purse updated → Next player presented → Repeat until all players sold

4. **Results Flow:**
   - All players sold → AI service calculates playing XI for each team → Impact players selected → Team ratings computed → Winner determined → Results displayed


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Username validation rejects empty inputs
*For any* username input that is empty or contains only whitespace, the system should reject it and prevent user entry.
**Validates: Requirements 1.2**

### Property 2: User-room association persistence
*For any* user who successfully joins a room, querying the system for that user's room should return the correct room identifier.
**Validates: Requirements 1.3**

### Property 3: Room code uniqueness
*For any* set of created rooms, all room codes should be distinct from each other.
**Validates: Requirements 2.1, 2.4**

### Property 4: Room capacity constraints
*For any* created room, the minimum participant count should be 5 and the maximum should be 10.
**Validates: Requirements 2.2, 2.3**

### Property 5: Invalid room code rejection
*For any* room code that does not exist in the system, join attempts should be rejected with an appropriate error.
**Validates: Requirements 3.1**

### Property 6: Participant list consistency
*For any* successful room join operation, the user should appear in the room's participant list immediately after joining.
**Validates: Requirements 3.3**

### Property 7: Real-time participant broadcast
*For any* user join event, all connected clients in that room should receive the updated participant list.
**Validates: Requirements 3.4**

### Property 8: Team name validation
*For any* team name input that is empty or contains only whitespace, the system should reject it.
**Validates: Requirements 4.2**

### Property 9: Logo file persistence
*For any* uploaded logo file, the system should store it and return a valid URL that can be used to retrieve the file.
**Validates: Requirements 4.3**

### Property 10: Purse amount validation
*For any* purse amount that is not a positive number, the system should reject it.
**Validates: Requirements 4.4**

### Property 11: Auction start precondition
*For any* room with fewer than 5 participants, attempting to start the auction should be rejected.
**Validates: Requirements 5.1**

### Property 12: Room state transition on auction start
*For any* room in lobby state with sufficient participants, starting the auction should transition the room to active state.
**Validates: Requirements 5.2**

### Property 13: Join prevention in active auctions
*For any* room in active state, join attempts should be rejected.
**Validates: Requirements 5.3**

### Property 14: Scraped player data completeness
*For any* player scraped from external sources, the data should include name, role, country, base price, batting statistics, and bowling statistics.
**Validates: Requirements 6.2**

### Property 15: Overall score computation
*For any* player with batting and bowling scores, an overall score should be computed and stored.
**Validates: Requirements 6.5**

### Property 16: Player presentation data completeness
*For any* player presented for auction, the display data should include name, role, country, base price, statistics, and overall rating.
**Validates: Requirements 7.1, 7.2**

### Property 17: Timer initialization on player presentation
*For any* player presented for auction, a 30-second countdown timer should be started.
**Validates: Requirements 7.3**

### Property 18: Bid increment consistency
*For any* current bid amount, placing a bid should increase it by exactly the configured bid increment.
**Validates: Requirements 8.1**

### Property 19: Purse sufficiency check
*For any* bid attempt, if the user's remaining purse is less than the bid amount, the bid should be rejected.
**Validates: Requirements 8.2**

### Property 20: Valid bid broadcast
*For any* valid bid placed, all connected clients in the room should receive the updated bid information.
**Validates: Requirements 8.4**

### Property 21: Player assignment on timer expiry
*For any* auction timer that reaches zero, the player should be assigned to the team with the highest bid.
**Validates: Requirements 8.5**

### Property 22: Purse deduction on player win
*For any* player won by a team, the team's purse should decrease by exactly the sold price.
**Validates: Requirements 9.1**

### Property 23: Sale record persistence
*For any* sold player, the database should contain a record with the sold price and winning team identifier.
**Validates: Requirements 9.2**

### Property 24: Team player record creation
*For any* player assigned to a team, a corresponding record should exist in the team_players table.
**Validates: Requirements 9.3**

### Property 25: Purse update broadcast
*For any* purse update, all connected clients in the room should receive the new purse value.
**Validates: Requirements 9.4**

### Property 26: Bid history broadcast
*For any* bid placed, all connected clients should see the bid added to the history display.
**Validates: Requirements 10.1**

### Property 27: Squad size increment on player acquisition
*For any* player sold to a team, that team's squad size should increase by exactly 1.
**Validates: Requirements 10.2**

### Property 28: Playing XI size constraint
*For any* team with at least 11 players, the selected playing XI should contain exactly 11 players.
**Validates: Requirements 11.1**

### Property 29: Playing XI composition constraints
*For any* selected playing XI, it should contain exactly 1 wicket-keeper, at least 3 batsmen, at least 2 bowlers, between 1 and 3 all-rounders, and at most 4 overseas players.
**Validates: Requirements 11.2, 11.3, 11.4, 11.5, 11.6**

### Property 30: Playing XI optimization
*For any* team, the selected playing XI should be a valid combination with the highest total overall score among all possible valid combinations.
**Validates: Requirements 11.7**

### Property 31: Bench player identification
*For any* team with a finalized playing XI, the bench players should be exactly those players in the squad who are not in the playing XI.
**Validates: Requirements 12.1**

### Property 32: Impact player selection
*For any* team, the impact player should be the bench player with the highest overall score.
**Validates: Requirements 12.2**

### Property 33: Impact player database marking
*For any* selected impact player, the team_players record should have is_impact_player set to true.
**Validates: Requirements 12.3**

### Property 34: Team rating components computation
*For any* team after auction completion, the system should compute batting rating, bowling rating, balance score, bench depth, and role coverage score.
**Validates: Requirements 13.1, 13.2, 13.3, 13.4, 13.5**

### Property 35: Overall rating formula application
*For any* team with component ratings, the overall rating should equal the weighted sum: 0.6 × avg_score_XI + 0.3 × balance_score + 0.1 × bench_depth.
**Validates: Requirements 13.6**

### Property 36: Rating normalization
*For any* computed team rating, the value should be in the range [0, 100].
**Validates: Requirements 13.7**

### Property 37: Winner determination
*For any* completed auction with multiple teams, the winning team should be the one with the highest overall rating.
**Validates: Requirements 14.1**

### Property 38: Results data completeness
*For any* completed auction, the results should include each team's name, logo, full squad, playing XI, impact player, and team rating.
**Validates: Requirements 15.1, 15.2, 15.3, 15.4, 15.5**

## Error Handling

### Input Validation Errors
- **Empty username**: Return 400 Bad Request with message "Username cannot be empty"
- **Empty team name**: Return 400 Bad Request with message "Team name cannot be empty"
- **Invalid purse amount**: Return 400 Bad Request with message "Purse must be a positive number"
- **Invalid room code**: Return 404 Not Found with message "Room not found"

### Business Logic Errors
- **Room at capacity**: Return 403 Forbidden with message "Room is full"
- **Insufficient participants**: Return 400 Bad Request with message "At least 5 participants required to start auction"
- **Insufficient purse**: Return 400 Bad Request with message "Insufficient purse for this bid"
- **Room already active**: Return 400 Bad Request with message "Cannot join active auction"
- **Unauthorized action**: Return 403 Forbidden with message "Only host can start auction"

### WebSocket Errors
- **Connection failure**: Emit 'error' event with message "Failed to connect to auction room"
- **Disconnection during auction**: Remove user from active bidders, notify other participants
- **Invalid event data**: Emit 'error' event with message "Invalid request data"

### External Service Errors
- **Scraping failure**: Log error, use fallback CSV data if available, otherwise return empty player list
- **File upload failure**: Return 500 Internal Server Error with message "Failed to upload logo"
- **Database connection failure**: Return 503 Service Unavailable with message "Database temporarily unavailable"

### Error Response Format
All API errors follow this structure:
```json
{
  "error": true,
  "message": "Human-readable error message",
  "code": "ERROR_CODE",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## Testing Strategy

### Unit Testing

Unit tests will verify individual functions and methods in isolation:

**Backend Unit Tests:**
- Room code generation uniqueness
- Username and team name validation logic
- Purse calculation and deduction
- Player overall score calculation
- Playing XI selection algorithm with various squad compositions
- Impact player selection logic
- Team rating calculation formulas
- Winner determination logic

**Frontend Unit Tests:**
- Component rendering with various props
- Form validation logic
- Timer countdown logic
- Data formatting functions

**Testing Framework:** pytest for Python backend, Jest + React Testing Library for frontend

### Property-Based Testing

Property-based tests will verify universal properties across many randomly generated inputs using **Hypothesis** (Python):

**Configuration:**
- Each property test will run a minimum of 100 iterations
- Tests will use custom strategies to generate valid domain objects (rooms, teams, players, bids)

**Property Test Coverage:**
- Username validation (Property 1)
- Room code uniqueness (Property 3)
- Room capacity constraints (Property 4)
- Purse deduction correctness (Property 22)
- Playing XI composition constraints (Property 29)
- Team rating normalization (Property 36)
- Winner determination (Property 37)

**Test Annotation Format:**
Each property-based test will include a comment tag:
```python
# Feature: ipl-mock-auction-arena, Property 3: Room code uniqueness
```

### Integration Testing

Integration tests will verify component interactions:
- Room creation → joining → auction start flow
- Bidding → player assignment → purse update flow
- Auction completion → playing XI selection → rating calculation flow
- WebSocket event broadcasting and reception
- Database persistence and retrieval

### End-to-End Testing

E2E tests will simulate complete user journeys:
- Create room → configure team → conduct auction → view results
- Multiple users bidding simultaneously
- Timer expiry and player assignment
- Results dashboard display

**Testing Framework:** Playwright or Selenium for browser automation

### WebSocket Testing

Real-time communication tests:
- Event emission and reception
- Broadcast to multiple clients
- Handling disconnections
- Message ordering and consistency

**Testing Framework:** python-socketio test client

### Performance Testing

- Load testing with 10 concurrent users in a room
- Stress testing with multiple simultaneous auctions
- Timer accuracy under load
- Database query performance with large player pools

## Implementation Notes

### Web Scraping Considerations
- Implement rate limiting to avoid overwhelming source websites
- Use caching to minimize repeated requests
- Include error handling for network failures
- Respect robots.txt and terms of service
- Provide fallback to pre-collected CSV data if scraping fails

### Real-Time Communication
- Use Socket.IO rooms feature to isolate auction room communications
- Implement heartbeat mechanism to detect disconnections
- Queue events during temporary disconnections
- Implement reconnection logic with state synchronization

### Playing XI Selection Algorithm
The algorithm uses a constraint satisfaction approach:
1. Generate all possible 11-player combinations from the squad
2. Filter combinations that violate role constraints
3. Filter combinations that violate overseas player limit
4. Rank remaining combinations by total overall score
5. Select the highest-ranked combination

For large squads, use optimization techniques:
- Greedy selection with backtracking
- Dynamic programming for subset selection
- Pruning invalid branches early

### Team Rating Formula
```
batting_rating = average(batting_scores of playing XI batsmen and all-rounders)
bowling_rating = average(bowling_scores of playing XI bowlers and all-rounders)
balance_score = min(batting_rating, bowling_rating) / max(batting_rating, bowling_rating) × 100
bench_depth = average(overall_scores of bench players)
role_coverage = (roles_covered / 4) × 100  # 4 roles: BAT, BOWL, AR, WK

overall_rating = 0.6 × avg_score_XI + 0.3 × balance_score + 0.1 × bench_depth
normalized_rating = (overall_rating / max_possible_score) × 100
```

### Security Considerations
- Validate all user inputs on server side
- Sanitize file uploads (logo images)
- Implement rate limiting on API endpoints
- Use CORS to restrict frontend origins
- Validate WebSocket event payloads
- Prevent SQL injection through parameterized queries (SQLAlchemy handles this)

### Scalability Considerations
- Use connection pooling for database
- Implement caching for player data
- Consider Redis for session management in production
- Use background tasks for heavy computations (playing XI selection)
- Implement pagination for large result sets

### Deployment Considerations
- Use environment variables for configuration
- Separate development and production databases
- Implement logging for debugging and monitoring
- Use WSGI server (Gunicorn) for production
- Serve static files through CDN or reverse proxy
- Implement health check endpoints
