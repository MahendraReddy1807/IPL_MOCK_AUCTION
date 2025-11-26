# Requirements Document

## Introduction

The IPL Mock Auction Arena is a multiplayer web application that simulates the Indian Premier League player auction experience. Users can create or join auction rooms, bid on players in real-time, and receive AI-based predictions for optimal team composition and performance ratings after the auction concludes.

## Glossary

- **Auction System**: The core system managing the IPL Mock Auction Arena application
- **User**: A participant in an auction room who bids on players
- **Auction Room**: A virtual space where multiple users conduct a player auction
- **Room Code**: A unique identifier for an auction room (e.g., IPL1234)
- **Host**: The user who creates an auction room
- **Player Pool**: The collection of IPL players available for bidding
- **Purse**: Virtual currency allocated to each team for purchasing players
- **Base Price**: The minimum starting bid for a player
- **Bid Increment**: The amount by which bids increase (X Lakhs)
- **Playing XI**: The 11 players selected as the starting lineup
- **Impact Player**: A substitute player selected from the bench
- **Team Rating**: A computed score representing overall team strength
- **Overall Score**: A calculated metric representing a player's combined performance value
- **Overseas Player**: A player from a country other than India
- **Role**: Player position category (BAT/BOWL/AR/WK)
- **BAT**: Batsman role
- **BOWL**: Bowler role
- **AR**: All-Rounder role
- **WK**: Wicket-Keeper role

## Requirements

### Requirement 1

**User Story:** As a user, I want to join an auction without creating an account, so that I can quickly participate in auctions.

#### Acceptance Criteria

1. WHEN a user accesses the application THEN the Auction System SHALL allow entry with only a username
2. WHEN a user provides a username THEN the Auction System SHALL validate that the username is non-empty
3. WHEN a user joins an auction room THEN the Auction System SHALL associate the username with that room session

### Requirement 2

**User Story:** As a user, I want to create an auction room, so that I can host an auction with my friends.

#### Acceptance Criteria

1. WHEN a user creates an auction room THEN the Auction System SHALL generate a unique room code
2. WHEN an auction room is created THEN the Auction System SHALL set the minimum participant count to 5 users
3. WHEN an auction room is created THEN the Auction System SHALL set the maximum participant count to 10 users
4. WHEN a room code is generated THEN the Auction System SHALL ensure the code is unique across all active rooms

### Requirement 3

**User Story:** As a user, I want to join an existing auction room using a room code, so that I can participate in an ongoing auction.

#### Acceptance Criteria

1. WHEN a user enters a room code THEN the Auction System SHALL validate that the room exists
2. WHEN a user attempts to join a full room THEN the Auction System SHALL reject the join request
3. WHEN a user successfully joins a room THEN the Auction System SHALL add the user to the room's participant list
4. WHEN a user joins a room THEN the Auction System SHALL broadcast the updated participant list to all room members

### Requirement 4

**User Story:** As a user in an auction room lobby, I want to configure my team details, so that I can personalize my team identity.

#### Acceptance Criteria

1. WHEN a user is in the lobby THEN the Auction System SHALL prompt for team name entry
2. WHEN a user provides a team name THEN the Auction System SHALL validate that the name is non-empty
3. WHERE a user chooses to upload a logo THEN the Auction System SHALL accept and store the logo file
4. WHEN a user sets their starting purse THEN the Auction System SHALL validate that the purse amount is a positive number
5. WHEN all users have configured their teams THEN the Auction System SHALL enable the host to start the auction

### Requirement 5

**User Story:** As a host, I want to start the auction when all participants are ready, so that we can begin bidding on players.

#### Acceptance Criteria

1. WHEN the host initiates auction start THEN the Auction System SHALL verify that at least 5 users have joined
2. WHEN the auction starts THEN the Auction System SHALL transition the room status from lobby to active
3. WHEN the auction becomes active THEN the Auction System SHALL prevent new users from joining

### Requirement 6

**User Story:** As a system administrator, I want player data to be automatically collected and stored, so that the auction has a comprehensive player pool.

#### Acceptance Criteria

1. WHEN the application starts THEN the Auction System SHALL execute a web scraping script to collect player data
2. WHEN scraping player data THEN the Auction System SHALL extract player name, role, country, base price, batting statistics, and bowling statistics
3. WHEN player data is collected THEN the Auction System SHALL save the data to a CSV file
4. WHEN the application initializes the database THEN the Auction System SHALL import player data from the CSV file
5. WHEN calculating player metrics THEN the Auction System SHALL compute an overall score for each player

### Requirement 7

**User Story:** As a user in an active auction, I want to see the current player being auctioned with their details, so that I can make informed bidding decisions.

#### Acceptance Criteria

1. WHEN a player is called for auction THEN the Auction System SHALL display the player name, role, country, base price, and statistics
2. WHEN displaying player statistics THEN the Auction System SHALL show the overall rating
3. WHEN a player is presented THEN the Auction System SHALL start a 30-second countdown timer

### Requirement 8

**User Story:** As a user, I want to place bids on players in real-time, so that I can acquire players for my team.

#### Acceptance Criteria

1. WHEN a user clicks the bid button THEN the Auction System SHALL increase the current bid by the bid increment
2. WHEN a bid is placed THEN the Auction System SHALL verify that the user's remaining purse is greater than or equal to the bid amount
3. IF a user's purse is insufficient THEN the Auction System SHALL reject the bid and maintain the current highest bid
4. WHEN a valid bid is placed THEN the Auction System SHALL broadcast the new highest bid to all room participants
5. WHEN the countdown timer reaches zero THEN the Auction System SHALL assign the player to the highest bidder

### Requirement 9

**User Story:** As a user, I want my team's purse to be updated after winning a bid, so that my available budget reflects my purchases.

#### Acceptance Criteria

1. WHEN a user wins a player THEN the Auction System SHALL deduct the sold price from the user's purse
2. WHEN a player is sold THEN the Auction System SHALL record the sold price and the winning team
3. WHEN a player is assigned to a team THEN the Auction System SHALL insert a record in the team players table
4. WHEN purse is updated THEN the Auction System SHALL broadcast the new purse value to all room participants

### Requirement 10

**User Story:** As a user, I want to see real-time updates of all bids and team information during the auction, so that I can track the auction progress.

#### Acceptance Criteria

1. WHEN any bid is placed THEN the Auction System SHALL update the bid history display for all users
2. WHEN a player is sold THEN the Auction System SHALL update the squad size for the winning team
3. WHILE the auction is active THEN the Auction System SHALL display each team's current purse and squad size

### Requirement 11

**User Story:** As a user, I want the system to automatically select my best playing XI after the auction, so that I can see my optimal team composition.

#### Acceptance Criteria

1. WHEN the auction concludes THEN the Auction System SHALL select 11 players from each team's squad
2. WHEN selecting playing XI THEN the Auction System SHALL include exactly 1 wicket-keeper
3. WHEN selecting playing XI THEN the Auction System SHALL include at least 3 batsmen
4. WHEN selecting playing XI THEN the Auction System SHALL include at least 2 bowlers
5. WHEN selecting playing XI THEN the Auction System SHALL include between 1 and 3 all-rounders
6. WHEN selecting playing XI THEN the Auction System SHALL include at most 4 overseas players
7. WHEN selecting playing XI THEN the Auction System SHALL rank players by overall score and select the highest-rated valid combination

### Requirement 12

**User Story:** As a user, I want the system to suggest an impact player from my bench, so that I know which substitute provides the most value.

#### Acceptance Criteria

1. WHEN playing XI is finalized THEN the Auction System SHALL identify all remaining bench players
2. WHEN selecting an impact player THEN the Auction System SHALL choose the highest-rated player not in the playing XI
3. WHEN an impact player is selected THEN the Auction System SHALL mark the player as the impact player in the database

### Requirement 13

**User Story:** As a user, I want to see my team's overall rating after the auction, so that I can understand my team's strength.

#### Acceptance Criteria

1. WHEN the auction ends THEN the Auction System SHALL compute a batting strength rating for each team
2. WHEN the auction ends THEN the Auction System SHALL compute a bowling strength rating for each team
3. WHEN the auction ends THEN the Auction System SHALL compute an all-rounder balance score for each team
4. WHEN the auction ends THEN the Auction System SHALL compute a bench depth score for each team
5. WHEN the auction ends THEN the Auction System SHALL compute a role coverage score for each team
6. WHEN computing overall rating THEN the Auction System SHALL apply weighted formula combining all component ratings
7. WHEN the overall rating is calculated THEN the Auction System SHALL normalize the rating to a scale of 0 to 100

### Requirement 14

**User Story:** As a user, I want to see which team won the auction, so that I can compare my team against the best team.

#### Acceptance Criteria

1. WHEN all team ratings are computed THEN the Auction System SHALL identify the team with the highest rating
2. WHEN the best team is determined THEN the Auction System SHALL display the winning team on the results dashboard

### Requirement 15

**User Story:** As a user, I want to view a comprehensive results dashboard after the auction, so that I can analyze all teams' compositions and ratings.

#### Acceptance Criteria

1. WHEN the auction concludes THEN the Auction System SHALL display each team's name and logo
2. WHEN displaying results THEN the Auction System SHALL show each team's full squad with player names and roles
3. WHEN displaying results THEN the Auction System SHALL highlight the playing XI for each team
4. WHEN displaying results THEN the Auction System SHALL show the impact player for each team
5. WHEN displaying results THEN the Auction System SHALL display the team rating for each team
6. WHERE visualization is supported THEN the Auction System SHALL render comparison charts for team ratings
