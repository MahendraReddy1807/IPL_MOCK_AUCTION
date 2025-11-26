# API Documentation

## REST API Endpoints

### Base URL
```
http://localhost:5000/api
```

All endpoints return JSON responses with appropriate HTTP status codes.

---

## Room Management

### Create Room
Creates a new auction room with a unique room code.

**Endpoint:** `POST /api/rooms/create`

**Request Body:**
```json
{
  "host_username": "string"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "room_code": "IPL1234",
  "status": "lobby"
}
```

**Error Responses:**
- `400 Bad Request` - Invalid username (empty or whitespace only)

---

### Join Room
Join an existing auction room using a room code.

**Endpoint:** `POST /api/rooms/join`

**Request Body:**
```json
{
  "room_code": "string",
  "username": "string"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "room_code": "IPL1234",
  "participants": []
}
```

**Error Responses:**
- `400 Bad Request` - Invalid username
- `404 Not Found` - Room does not exist
- `403 Forbidden` - Room is full (max 10 participants)
- `400 Bad Request` - Room is already active

---

### Get Room Details
Retrieve details about a specific room.

**Endpoint:** `GET /api/rooms/{code}`

**Success Response (200):**
```json
{
  "room_code": "IPL1234",
  "status": "lobby",
  "host_username": "player1",
  "participants": [],
  "min_users": 5,
  "max_users": 10
}
```

---

## Team Management

### Configure Team
Configure team details including name, logo, and starting purse.

**Endpoint:** `POST /api/teams/configure`

**Request Body:**
```json
{
  "room_code": "string",
  "username": "string",
  "team_name": "string",
  "purse": 100.0
}
```

**Success Response (200):**
```json
{
  "success": true,
  "team_id": 1,
  "team_name": "Mumbai Indians",
  "purse": 100.0
}
```

---

### Upload Team Logo
Upload a logo image for a team.

**Endpoint:** `POST /api/teams/upload-logo`

**Request Body:** `multipart/form-data`
- `logo` (file) - Image file (PNG, JPG, JPEG)
- `team_id` (string) - Team ID

**Success Response (200):**
```json
{
  "success": true,
  "logo_url": "/uploads/logos/team_1_logo.png"
}
```

---

## Player Management

### Get All Players
Retrieve the complete list of players available for auction.

**Endpoint:** `GET /api/players`

**Success Response (200):**
```json
{
  "players": [
    {
      "id": 1,
      "name": "Virat Kohli",
      "role": "BAT",
      "country": "India",
      "base_price": 2.0,
      "overall_score": 88.5,
      "is_overseas": false
    }
  ]
}
```

---

## Auction Management

### Get Auction State
Retrieve the current state of an active auction.

**Endpoint:** `GET /api/auction/{room_code}/state`

**Success Response (200):**
```json
{
  "room_code": "IPL1234",
  "status": "active",
  "current_player": {},
  "current_bid": 5.5,
  "highest_bidder": "player2",
  "teams": []
}
```

---

## Results

### Get Auction Results
Retrieve comprehensive results after auction completion.

**Endpoint:** `GET /api/results/{room_code}`

**Success Response (200):**
```json
{
  "room_code": "IPL1234",
  "winner": {
    "team_id": 1,
    "team_name": "Mumbai Indians",
    "overall_rating": 87.5
  },
  "teams": []
}
```

---

## WebSocket Events

The application uses Socket.IO for real-time bidirectional communication.

### Connection
```javascript
import io from 'socket.io-client';
const socket = io('http://localhost:5000');
```

---

## Client → Server Events

### join_room
**Data:**
```json
{
  "room_code": "IPL1234",
  "username": "player1"
}
```

### place_bid
**Data:**
```json
{
  "room_code": "IPL1234",
  "username": "player1"
}
```

### start_auction
**Data:**
```json
{
  "room_code": "IPL1234"
}
```

---

## Server → Client Events

### user_joined
**Data:**
```json
{
  "username": "player2",
  "participants_count": 6
}
```

### player_presented
**Data:**
```json
{
  "player": {},
  "timer_duration": 30,
  "current_bid": 2.0
}
```

### bid_placed
**Data:**
```json
{
  "username": "player2",
  "bid_amount": 5.5,
  "current_highest": "player2"
}
```

### player_sold
**Data:**
```json
{
  "player": {},
  "sold_to": "player2",
  "sold_price": 5.5
}
```

### purse_updated
**Data:**
```json
{
  "team_id": 2,
  "new_purse": 84.5,
  "squad_size": 3
}
```

### auction_completed
**Data:**
```json
{
  "message": "Auction completed",
  "room_code": "IPL1234"
}
```

### error
**Data:**
```json
{
  "message": "Error message"
}
```

---

## Error Response Format

```json
{
  "error": true,
  "message": "Human-readable error message"
}
```

### HTTP Status Codes
- `200 OK` - Request successful
- `400 Bad Request` - Invalid input
- `403 Forbidden` - Unauthorized action
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

---

## Example Usage

### JavaScript Example
```javascript
import axios from 'axios';
import io from 'socket.io-client';

const API_URL = 'http://localhost:5000/api';
const socket = io('http://localhost:5000');

// Create room
const response = await axios.post(`${API_URL}/rooms/create`, {
  host_username: 'player1'
});

// Join room via WebSocket
socket.emit('join_room', {
  room_code: 'IPL1234',
  username: 'player1'
});

// Listen for events
socket.on('player_presented', (data) => {
  console.log('New player:', data.player);
});
```

---

## Testing with cURL

```bash
# Create a room
curl -X POST http://localhost:5000/api/rooms/create \
  -H "Content-Type: application/json" \
  -d '{"host_username": "player1"}'

# Get all players
curl http://localhost:5000/api/players
```

---

## Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Flask-SocketIO Documentation](https://flask-socketio.readthedocs.io/)
- [Socket.IO Client Documentation](https://socket.io/docs/v4/client-api/)
- [React Documentation](https://react.dev/)
