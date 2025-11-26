# Requirements Document

## Introduction

This specification defines the conversion of the IPL Mock Auction Arena from a Flask backend + React frontend architecture to a unified Streamlit application. The conversion will maintain all core auction functionality while leveraging Streamlit's built-in features for rapid deployment and simplified architecture.

## Glossary

- **Streamlit Application**: The unified Python-based web application framework that combines backend logic and frontend UI
- **Session State**: Streamlit's mechanism for maintaining state across user interactions and page reruns
- **Auction System**: The core system managing the IPL Mock Auction Arena application
- **User**: A participant in an auction room who bids on players
- **Auction Room**: A virtual space where multiple users conduct a player auction
- **Room Code**: A unique identifier for an auction room (e.g., IPL1234)
- **Host**: The user who creates an auction room
- **Player Pool**: The collection of IPL players available for bidding
- **Purse**: Virtual currency allocated to each team for purchasing players
- **Base Price**: The minimum starting bid for a player
- **Playing XI**: The 11 players selected as the starting lineup
- **Impact Player**: A substitute player selected from the bench
- **Team Rating**: A computed score representing overall team strength
- **SQLite Database**: The embedded database for persisting auction data
- **Real-time Updates**: Automatic UI refresh mechanism for multi-user synchronization
- **Deployment Platform**: Cloud hosting service for the Streamlit application (Streamlit Cloud, Heroku, or Render)

## Requirements

### Requirement 1

**User Story:** As a developer, I want to convert the Flask backend to Streamlit, so that I have a unified Python application with simplified architecture.

#### Acceptance Criteria

1. WHEN converting the backend THEN the Auction System SHALL preserve all SQLAlchemy models from the original application
2. WHEN converting the backend THEN the Auction System SHALL migrate all service layer logic to Streamlit-compatible functions
3. WHEN converting the backend THEN the Auction System SHALL maintain the SQLite database schema
4. WHEN converting the backend THEN the Auction System SHALL remove Flask-specific dependencies including Flask-SocketIO and Flask-CORS
5. WHEN converting the backend THEN the Auction System SHALL replace REST API endpoints with Streamlit session state and callbacks

### Requirement 2

**User Story:** As a developer, I want to convert the React frontend to Streamlit UI components, so that I have a Python-only codebase.

#### Acceptance Criteria

1. WHEN converting the frontend THEN the Auction System SHALL recreate the Home page using Streamlit widgets
2. WHEN converting the frontend THEN the Auction System SHALL recreate the Lobby page using Streamlit widgets
3. WHEN converting the frontend THEN the Auction System SHALL recreate the AuctionRoom page using Streamlit widgets
4. WHEN converting the frontend THEN the Auction System SHALL recreate the Results page using Streamlit widgets
5. WHEN converting the frontend THEN the Auction System SHALL remove all React, Vite, and Node.js dependencies

### Requirement 3

**User Story:** As a user, I want to access the application through a single Streamlit interface, so that I can participate in auctions without complex setup.

#### Acceptance Criteria

1. WHEN a user accesses the application THEN the Auction System SHALL display a navigation sidebar for page selection
2. WHEN a user navigates between pages THEN the Auction System SHALL preserve session state across page transitions
3. WHEN the application loads THEN the Auction System SHALL initialize the database connection
4. WHEN the application loads THEN the Auction System SHALL load player data from the CSV file if the database is empty

### Requirement 4

**User Story:** As a user, I want to create or join auction rooms through the Streamlit interface, so that I can start or participate in auctions.

#### Acceptance Criteria

1. WHEN a user enters a username THEN the Auction System SHALL store the username in session state
2. WHEN a user creates a room THEN the Auction System SHALL generate a unique room code and store it in the database
3. WHEN a user joins a room THEN the Auction System SHALL validate the room code against existing rooms
4. WHEN a user joins a room THEN the Auction System SHALL add the user to the room's participant list in the database
5. WHEN a user is in a room THEN the Auction System SHALL display the room code prominently

### Requirement 5

**User Story:** As a user, I want to configure my team in the lobby, so that I can set my team name, logo, and starting purse before the auction begins.

#### Acceptance Criteria

1. WHEN a user is in the lobby THEN the Auction System SHALL display input fields for team name and starting purse
2. WHEN a user uploads a team logo THEN the Auction System SHALL save the logo file and associate it with the team
3. WHEN a user submits team configuration THEN the Auction System SHALL validate that the team name is unique within the room
4. WHEN a user submits team configuration THEN the Auction System SHALL validate that the purse amount is within acceptable limits
5. WHEN all users configure their teams THEN the Auction System SHALL enable the host to start the auction

### Requirement 6

**User Story:** As a host, I want to start the auction when all participants are ready, so that the bidding process can begin.

#### Acceptance Criteria

1. WHEN the host is in the lobby THEN the Auction System SHALL display a start auction button
2. WHEN the host clicks start auction THEN the Auction System SHALL validate that all participants have configured their teams
3. WHEN the host starts the auction THEN the Auction System SHALL update the room status to "in_progress" in the database
4. WHEN the auction starts THEN the Auction System SHALL present the first player from the player pool
5. WHEN the auction starts THEN the Auction System SHALL initialize a 30-second countdown timer

### Requirement 7

**User Story:** As a user, I want to place bids on players during the auction, so that I can build my team.

#### Acceptance Criteria

1. WHEN a player is presented THEN the Auction System SHALL display player details including name, role, and base price
2. WHEN a user clicks the bid button THEN the Auction System SHALL increment the current bid by the minimum bid increment
3. WHEN a user places a bid THEN the Auction System SHALL validate that the user has sufficient purse balance
4. WHEN a bid is placed THEN the Auction System SHALL update the current highest bidder in the database
5. WHEN the timer expires THEN the Auction System SHALL assign the player to the highest bidder and deduct the bid amount from their purse

### Requirement 8

**User Story:** As a user, I want to see real-time updates during the auction, so that I know the current bid status and remaining time.

#### Acceptance Criteria

1. WHEN the auction is in progress THEN the Auction System SHALL display the current highest bid and bidder
2. WHEN the auction is in progress THEN the Auction System SHALL display the remaining time for the current player
3. WHEN a bid is placed THEN the Auction System SHALL refresh the UI to show the updated bid information
4. WHEN the timer reaches zero THEN the Auction System SHALL automatically move to the next player
5. WHEN all players are sold THEN the Auction System SHALL update the room status to "completed" and navigate to results

### Requirement 9

**User Story:** As a user, I want to view auction results with team ratings and playing XI, so that I can see how my team performed.

#### Acceptance Criteria

1. WHEN the auction completes THEN the Auction System SHALL calculate team ratings for all teams
2. WHEN the auction completes THEN the Auction System SHALL determine the playing XI for each team
3. WHEN viewing results THEN the Auction System SHALL display the winning team with the highest rating
4. WHEN viewing results THEN the Auction System SHALL display all teams with their total ratings and squad lists
5. WHEN viewing results THEN the Auction System SHALL display detailed rating breakdowns for batting, bowling, and fielding

### Requirement 10

**User Story:** As a developer, I want to implement automatic page refresh for multi-user synchronization, so that all users see consistent auction state.

#### Acceptance Criteria

1. WHEN multiple users are in the same room THEN the Auction System SHALL use Streamlit's auto-refresh mechanism to synchronize state
2. WHEN the auction state changes THEN the Auction System SHALL trigger a page rerun for all connected users
3. WHEN a user places a bid THEN the Auction System SHALL update the database and trigger UI refresh for all participants
4. WHEN the timer expires THEN the Auction System SHALL update all users' views simultaneously
5. WHEN a user joins or leaves THEN the Auction System SHALL update the participant list for all users in the room

### Requirement 11

**User Story:** As a developer, I want to deploy the Streamlit application to a cloud platform, so that users can access it without local setup.

#### Acceptance Criteria

1. WHEN deploying the application THEN the Auction System SHALL include a requirements.txt file with all Python dependencies
2. WHEN deploying the application THEN the Auction System SHALL include a streamlit configuration file for deployment settings
3. WHEN deploying to Streamlit Cloud THEN the Auction System SHALL configure the repository connection and branch
4. WHEN the application is deployed THEN the Auction System SHALL initialize the database on first run
5. WHEN the application is deployed THEN the Auction System SHALL be accessible via a public URL

### Requirement 12

**User Story:** As a developer, I want to maintain the AI service for team analysis, so that automatic playing XI selection and ratings work correctly.

#### Acceptance Criteria

1. WHEN the auction completes THEN the Auction System SHALL invoke the AI service to analyze each team
2. WHEN analyzing a team THEN the Auction System SHALL select the optimal playing XI based on player roles and ratings
3. WHEN analyzing a team THEN the Auction System SHALL calculate batting, bowling, and fielding ratings
4. WHEN analyzing a team THEN the Auction System SHALL identify the impact player from the bench
5. WHEN analysis completes THEN the Auction System SHALL store the results in the team_rating table

### Requirement 13

**User Story:** As a user, I want the application to handle errors gracefully, so that I receive clear feedback when something goes wrong.

#### Acceptance Criteria

1. WHEN an error occurs THEN the Auction System SHALL display a user-friendly error message using Streamlit's error widget
2. WHEN a database operation fails THEN the Auction System SHALL log the error and display a generic error message
3. WHEN a user enters invalid input THEN the Auction System SHALL display validation errors inline with the input field
4. WHEN the database is locked THEN the Auction System SHALL retry the operation with exponential backoff
5. WHEN a critical error occurs THEN the Auction System SHALL provide an option to return to the home page

### Requirement 14

**User Story:** As a developer, I want to preserve the existing player database and scraper functionality, so that player data remains accurate and up-to-date.

#### Acceptance Criteria

1. WHEN the application starts THEN the Auction System SHALL load player data from the SQLite database
2. WHEN the database is empty THEN the Auction System SHALL import players from the CSV file
3. WHEN importing players THEN the Auction System SHALL validate player data including name, role, and base price
4. WHEN the scraper is invoked THEN the Auction System SHALL fetch updated player statistics from external sources
5. WHEN player data is updated THEN the Auction System SHALL persist changes to the database