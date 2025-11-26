# Implementation Plan

- [x] 1. Set up project structure and dependencies





  - Create backend directory structure (app, models, services, routes, utils)
  - Create frontend directory structure (src, components, pages, services)
  - Initialize Flask application with blueprints
  - Set up SQLAlchemy with SQLite database
  - Configure Flask-SocketIO for WebSocket support
  - Initialize React application with TailwindCSS
  - Create requirements.txt with all Python dependencies
  - Create package.json with all Node dependencies
  - Set up environment configuration files
  - _Requirements: 1.1, 2.1, 3.1_

- [x] 2. Implement database models and schema






  - Create User model with username and room association
  - Create Room model with code, status, and participant constraints
  - Create Team model with name, logo, and purse tracking
  - Create Player model with role, statistics, and overseas flag
  - Create AuctionPlayer model for room-specific player state
  - Create TeamPlayer model with playing XI and impact player flags
  - Create TeamRating model for storing computed ratings
  - Implement database initialization and migration scripts
  - _Requirements: 1.3, 2.1, 2.2, 2.3, 4.1, 6.2, 9.2, 9.3, 13.1_


- [x] 2.1 Write property test for room capacity constraints



  - **Property 4: Room capacity constraints**
  - **Validates: Requirements 2.2, 2.3**


- [x] 2.2 Write property test for purse validation



  - **Property 10: Purse amount validation**






  - **Validates: Requirements 4.4**
-

- [x] 3. Implement web scraping module for player data







  - Create scraper script using BeautifulSoup and Requests



  - Implement player data extraction (name, role, country, base price, stats)
  - Calculate batting and bowling scores from raw statistics
  - Compute overall player score based on role and statistics
  - Save scraped data to CSV file
  - Implement CSV import function to populate database
  - Add error handling and fallback to existing CSV data





  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 3.1 Write property test for scraped data completeness



  - **Property 14: Scraped player data completeness**
  - **Validates: Requirements 6.2**



- [x] 3.2 Write property test for overall score computation



  - **Property 15: Overall score computation**
  - **Validates: Requirements 6.5**

- [x] 4. Implement room management service




  - Create function to generate unique room codes
  - Implement room creation with host assignment
  - Implement room joining with capacity validation
  - Add participant list retrieval
  - Implement room state transitions (lobby → active → completed)
  - Add validation for minimum participants before auction start
  - Prevent joining active or completed rooms
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 3.3, 5.1, 5.2, 5.3_

- [x] 4.1 Write property test for room code uniqueness











  - **Property 3: Room code uniqueness**
  - **Validates: Requirements 2.1, 2.4**

- [x] 4.2 Write property test for invalid room code rejection


  - **Property 5: Invalid room code rejection**
  - **Validates: Requirements 3.1**

- [x] 4.3 Write property test for participant list consistency


  - **Property 6: Participant list consistency**
  - **Validates: Requirements 3.3**

- [x] 4.4 Write property test for auction start precondition


  - **Property 11: Auction start precondition**
  - **Validates: Requirements 5.1**

- [x] 4.5 Write property test for room state transition


  - **Property 12: Room state transition on auction start**
  - **Validates: Requirements 5.2**

- [x] 4.6 Write property test for join prevention in active auctions


  - **Property 13: Join prevention in active auctions**
  - **Validates: Requirements 5.3**

- [x] 5. Implement team service





  - Create team configuration function (name, logo URL, purse)
  - Implement logo file upload and storage
  - Add purse update function with validation
  - Implement add player to team function
  - Create get team squad function
  - Add validation for team name (non-empty)
  - Add validation for purse amount (positive number)
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 9.1, 9.3_

- [x] 5.1 Write property test for username validation


  - **Property 1: Username validation rejects empty inputs**
  - **Validates: Requirements 1.2**

- [x] 5.2 Write property test for team name validation


  - **Property 8: Team name validation**
  - **Validates: Requirements 4.2**

- [x] 5.3 Write property test for logo file persistence


  - **Property 9: Logo file persistence**

  - **Validates: Requirements 4.3**

- [x] 5.4 Write property test for purse deduction


  - **Property 22: Purse deduction on player win**
  - **Validates: Requirements 9.1**


- [x] 6. Implement auction engine core logic






  - Create function to present next player for auction
  - Implement countdown timer management (30 seconds)
  - Create bid placement function with purse validation
  - Implement bid increment logic
  - Add highest bidder tracking
  - Implement player assignment on timer expiry
  - Update team purse after player purchase
  - Record sold player information in database
  - Track auction progress and completion
  - _Requirements: 7.1, 7.2, 7.3, 8.1, 8.2, 8.3, 8.4, 8.5, 9.1, 9.2, 9.3_

- [x] 6.1 Write property test for player presentation data completeness


  - **Property 16: Player presentation data completeness**
  - **Validates: Requirements 7.1, 7.2**

- [x] 6.2 Write property test for timer initialization


  - **Property 17: Timer initialization on player presentation**
  - **Validates: Requirements 7.3**

- [x] 6.3 Write property test for bid increment consistency



  - **Property 18: Bid increment consistency**
  - **Validates: Requirements 8.1**

- [x] 6.4 Write property test for purse sufficiency check


  - **Property 19: Purse sufficiency check**
  - **Validates: Requirements 8.2**

- [x] 6.5 Write property test for player assignment on timer expiry


  - **Property 21: Player assignment on timer expiry**
  - **Validates: Requirements 8.5**

- [x] 6.6 Write property test for sale record persistence



  - **Property 23: Sale record persistence**

  - **Validates: Requirements 9.2**

- [x] 6.7 Write property test for team player record creation


  - **Property 24: Team player record creation**
  - **Validates: Requirements 9.3**

- [x] 7. Implement WebSocket event handlers






  - Set up Socket.IO server with Flask-SocketIO
  - Implement join_room event handler
  - Implement place_bid event handler
  - Implement start_auction event handler
  - Create broadcast functions for user_joined events
  - Create broadcast functions for player_presented events
  - Create broadcast functions for bid_placed events
  - Create broadcast functions for player_sold events
  - Create broadcast functions for purse_updated events
  - Create broadcast functions for auction_completed events
  - Handle client disconnections gracefully
  - _Requirements: 3.4, 8.4, 9.4, 10.1_

- [x] 7.1 Write property test for real-time participant broadcast


  - **Property 7: Real-time participant broadcast**
  - **Validates: Requirements 3.4**

- [x] 7.2 Write property test for valid bid broadcast

  - **Property 20: Valid bid broadcast**
  - **Validates: Requirements 8.4**

- [x] 7.3 Write property test for purse update broadcast

  - **Property 25: Purse update broadcast**
  - **Validates: Requirements 9.4**

- [x] 7.4 Write property test for bid history broadcast


  - **Property 26: Bid history broadcast**
  - **Validates: Requirements 10.1**
-

- [x] 8. Implement AI analysis service for playing XI selection





  - Create function to generate all valid 11-player combinations
  - Implement constraint validation (1 WK, 3+ BAT, 2+ BOWL, 1-3 AR, max 4 overseas)
  - Implement scoring function for combinations
  - Create optimization algorithm to select highest-scoring valid combination
  - Mark selected players as in_playing_xi in database
  - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7_

- [x] 8.1 Write property test for playing XI size constraint


  - **Property 28: Playing XI size constraint**
  - **Validates: Requirements 11.1**


- [x] 8.2 Write property test for playing XI composition constraints

  - **Property 29: Playing XI composition constraints**
  - **Validates: Requirements 11.2, 11.3, 11.4, 11.5, 11.6**

- [x] 8.3 Write property test for playing XI optimization


  - **Property 30: Playing XI optimization**
  - **Validates: Requirements 11.7**

- [x] 9. Implement impact player selection



  - Create function to identify bench players (not in playing XI)
  - Implement selection of highest-rated bench player
  - Mark selected player as is_impact_player in database
  - _Requirements: 12.1, 12.2, 12.3_

- [x] 9.1 Write property test for bench player identification


  - **Property 31: Bench player identification**
  - **Validates: Requirements 12.1**



- [x] 9.2 Write property test for impact player selection




  - **Property 32: Impact player selection**


  - **Validates: Requirements 12.2**



- [x] 9.3 Write property test for impact player database marking


  - **Property 33: Impact player database marking**
  - **Validates: Requirements 12.3**


- [x] 10. Implement team rating calculation engine






  - Create function to calculate batting strength rating
  - Create function to calculate bowling strength rating

  - Create function to calculate all-rounder balance score
  - Create function to calculate bench depth score


  - Create function to calculate role coverage score
  - Implement weighted formula for overall rating


  - Implement rating normalization to 0-100 scale
  - Store all ratings in TeamRating table


  - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.6, 13.7_




- [x] 10.1 Write property test for team rating components computation


  - **Property 34: Team rating components computation**
  - **Validates: Requirements 13.1, 13.2, 13.3, 13.4, 13.5**

- [x] 10.2 Write property test for overall rating formula


  - **Property 35: Overall rating formula application**
  - **Validates: Requirements 13.6**

- [x] 10.3 Write property test for rating normalization


  - **Property 36: Rating normalization**
  - **Validates: Requirements 13.7**

- [x] 11. Implement winner determination logic






  - Create function to retrieve all team ratings for a room
  - Implement logic to identify team with highest rating
  - Return winning team information
  - _Requirements: 14.1, 14.2_

- [x] 11.1 Write property test for winner determination


  - **Property 37: Winner determination**
  - **Validates: Requirements 14.1**
- [x] 12. Implement REST API endpoints







- [ ] 12. Implement REST API endpoints




  - Create POST /api/rooms/create endpoint
  - Create POST /api/rooms/join endpoint
  - Create GET /api/rooms/{code} endpoint
  - Create POST /api/teams/configure endpoint
  - Create POST /api/teams/upload-logo endpoint with file handling
  - Create GET /api/players endpoint
  - Create GET /api/auction/{room_code}/state endpoint
  - Create GET /api/results/{room_code} endpoint
  - Add input validation and error handling for all endpoints
  - Implement CORS configuration
  - _Requirements: 2.1, 3.1, 4.1, 4.3, 6.4, 15.1_

- [x] 12.1 Write integration tests for API endpoints


  - Test room creation and joining flow
  - Test team configuration flow
  - Test auction state retrieval
  - Test results retrieval


- [x] 13. Build frontend Home page component



  - Create React component for home page
  - Add create room button with click handler
  - Add join room input field and button
  - Implement API calls to backend
  - Add navigation to lobby page after room creation/joining
  - Style with TailwindCSS
  - _Requirements: 2.1, 3.1_

- [x] 14. Build frontend Lobby page component





  - Create React component for lobby page
  - Display room code prominently
  - Show list of joined participants with real-time updates
  - Create team configuration form (name, logo upload, purse)
  - Implement Socket.IO connection for real-time updates
  - Add start auction button (visible only to host)
  - Handle user_joined events from server
  - Navigate to auction room when auction starts
  - Style with TailwindCSS
  - _Requirements: 3.4, 4.1, 4.2, 4.3, 4.4, 5.1_

- [x] 15. Build frontend Auction Room page component





  - Create React component for auction room
  - Display current player card with all details
  - Implement countdown timer display with real-time updates
  - Create bid button with click handler
  - Display bid history panel
  - Create teams sidebar showing purse and squad size
  - Handle player_presented events from server
  - Handle bid_placed events from server
  - Handle player_sold events from server
  - Handle purse_updated events from server
  - Emit place_bid events to server
  - Style with TailwindCSS for modern appearance
  - _Requirements: 7.1, 7.2, 7.3, 8.1, 10.1, 10.2, 10.3_

- [x] 16. Build frontend Results Dashboard page component






  - Create React component for results dashboard
  - Display all teams with names and logos
  - Show full squad for each team
  - Highlight playing XI players
  - Display impact player with indicator
  - Show team ratings
  - Display winner announcement
  - Create comparison visualization (bar charts or radar charts)
  - Fetch results data from API
  - Style with TailwindCSS
  - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5, 15.6_

- [x] 16.1 Write property test for results data completeness


  - **Property 38: Results data completeness**
  - **Validates: Requirements 15.1, 15.2, 15.3, 15.4, 15.5**

- [x] 17. Implement frontend Socket.IO client service



  - Create Socket.IO client connection manager
  - Implement event emission functions
  - Implement event listener registration
  - Handle connection and disconnection
  - Add reconnection logic
  - _Requirements: 3.4, 8.4, 9.4, 10.1_

- [x] 18. Add error handling and validation throughout application



  - Implement input validation error responses
  - Add business logic error responses
  - Implement WebSocket error handling
  - Add external service error handling
  - Create consistent error response format
  - Add user-friendly error messages in frontend
  - _Requirements: 1.2, 3.1, 3.2, 4.2, 4.4, 5.1, 8.2, 8.3_

- [x] 19. Create sample data and seed script



  - Create sample player CSV with diverse roles and statistics
  - Implement database seed script for development
  - Add sample room and team data for testing
  - _Requirements: 6.3, 6.4_

- [x] 20. Write application documentation





  - Create README with project overview
  - Document installation instructions
  - Document how to run the application (backend and frontend)
  - Document API endpoints
  - Document WebSocket events
  - Document environment variables
  - Create requirements.txt with all dependencies
  - _Requirements: All_
-

- [x] 21. Final checkpoint - Ensure all tests pass





  - Ensure all tests pass, ask the user if questions arise.
