# Implementation Plan

- [x] 1. Set up Streamlit project structure



  - Create `streamlit_app/` directory with subdirectories for models, services, pages, utils, and data
  - Create `app.py` as main entry point
  - Create `config.py` for configuration settings
  - Create `.streamlit/config.toml` for Streamlit configuration


  - _Requirements: 1.1, 1.2, 1.3_

- [x] 2. Migrate database models and initialize database
  - Copy all SQLAlchemy model files from `backend/app/models/` to `streamlit_app/models/`
  - Create `models/__init__.py` to export all models


  - Implement database initialization in `app.py`
  - Copy `players.csv` to `streamlit_app/data/`
  - _Requirements: 1.1, 1.3, 3.3, 14.1, 14.2_

- [x] 3. Migrate service layer
  - Copy `room_service.py` from backend to `streamlit_app/services/`
  - Copy `team_service.py` from backend to `streamlit_app/services/`


  - Copy `auction_service.py` from backend to `streamlit_app/services/`
  - Copy `ai_service.py` from backend to `streamlit_app/services/`
  - Create `data_service.py` for CSV loading and database seeding
  - Update imports in all service files to use new structure

  - _Requirements: 1.2, 12.1, 12.2, 12.3, 12.4, 14.3, 14.4_

- [x] 4. Create utility modules
  - Implement `utils/validation.py` with username, team name, purse, and room code validation
  - Implement `utils/db_utils.py` with database session management and retry logic
  - Implement `utils/timer.py` with timer calculation and expiry checking functions


  - _Requirements: 13.3, 13.4_

- [x] 5. Implement main application entry point
  - Create `app.py` with database initialization function
  - Implement session state initialization
  - Create sidebar navigation with page selection
  - Add page routing logic based on session state


  - _Requirements: 3.1, 3.2, 3.3_

- [x] 6. Implement Home page
  - Create `pages/home.py` module
  - Add username input field with validation
  - Add "Create Room" button with room creation logic
  - Add "Join Room" section with room code input and join button
  - Display room code after successful creation


  - Store username, room_code, and is_host in session state
  - _Requirements: 2.1, 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 7. Implement Lobby page
  - Create `pages/lobby.py` module
  - Display room code prominently at top
  - Show real-time participant list

  - Add team configuration form (team name input, logo uploader, purse input)
  - Implement team configuration submission with validation
  - Add "Start Auction" button (visible only to host)
  - Implement database polling for participant updates
  - _Requirements: 2.2, 5.1, 5.2, 5.3, 5.4, 5.5, 6.1, 6.2, 10.5_

- [x] 8. Implement Auction page core functionality

  - Create `pages/auction.py` module
  - Display current player details (name, role, base price, stats)
  - Show current bid and highest bidder
  - Display countdown timer
  - Show user's remaining purse
  - Add "Place Bid" button
  - _Requirements: 2.3, 7.1, 8.1, 8.2_


- [x] 9. Implement auction bidding logic
  - Implement bid placement with purse validation
  - Update database on successful bid
  - Handle bid rejection with error messages
  - Implement timer expiry detection and player assignment


  - Auto-advance to next player after timer expiry
  - _Requirements: 7.2, 7.3, 7.4, 7.5, 8.4_

- [x] 10. Implement auction synchronization
  - Add database polling every 2-3 seconds
  - Detect state changes (current player, bid, bidder, timer)
  - Trigger page rerun on state changes
  - Update session state with latest database values

  - Handle timer synchronization across users
  - _Requirements: 8.3, 10.1, 10.2, 10.3, 10.4_

- [x] 11. Implement auction completion
  - Detect when all players are sold
  - Update room status to "completed"
  - Trigger AI analysis for all teams



  - Navigate to results page automatically
  - _Requirements: 8.5, 9.1, 9.2_

- [x] 12. Implement Results page


  - Create `pages/results.py` module
  - Display winner announcement with team name and rating
  - Show team ratings comparison bar chart
  - Display all teams with their squads
  - Show playing XI for each team
  - Show impact player for each team


  - Display rating breakdown (batting, bowling, balance, bench depth)
  - _Requirements: 2.4, 9.3, 9.4, 9.5_

- [x] 13. Implement error handling
  - Add try-catch blocks around database operations


  - Implement retry logic for database locks
  - Display user-friendly error messages using st.error()
  - Add validation error messages inline with inputs
  - Implement fallback to home page on critical errors
  - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5_

- [x] 14. Create deployment configuration
  - Create `requirements.txt` with all Python dependencies
  - Create `.streamlit/config.toml` with server and theme settings
  - Create `README.md` with setup and deployment instructions



  - Create `.gitignore` for Python and Streamlit
  - _Requirements: 11.1, 11.2_

- [x] 15. Test and deploy to Streamlit Cloud
  - Test application locally with multiple users
  - Create GitHub repository and push code
  - Connect repository to Streamlit Cloud
  - Configure deployment settings
  - Deploy and verify functionality
  - _Requirements: 11.3, 11.4, 11.5_

- [x] 16. Write unit tests for services
  - Write unit tests for room_service functions
  - Write unit tests for team_service functions
  - Write unit tests for auction_service functions
  - Write unit tests for ai_service functions
  - Write unit tests for validation functions

- [x] 17. Write property-based tests
  - **Property 1: Room code uniqueness** - **Validates: Requirements 1.2, 4.2**
  - **Property 2: Session state persistence** - **Validates: Requirements 3.2**
  - **Property 3: Team name uniqueness** - **Validates: Requirements 5.3**
  - **Property 4: Purse deduction correctness** - **Validates: Requirements 7.5**
  - **Property 5: Sufficient purse validation** - **Validates: Requirements 7.3**
  - **Property 6: Playing XI composition constraints** - **Validates: Requirements 12.2**
  - **Property 7: Timer expiry player assignment** - **Validates: Requirements 7.5, 8.4**
  - **Property 8: Auction completion detection** - **Validates: Requirements 8.5**
  - **Property 9: Winner determination correctness** - **Validates: Requirements 9.3**
  - **Property 10: Database state consistency** - **Validates: Requirements 10.1, 10.3**

- [x] 18. Write integration tests
  - Write end-to-end test for complete auction flow
  - Write test for multi-user synchronization
  - Write test for error recovery scenarios
