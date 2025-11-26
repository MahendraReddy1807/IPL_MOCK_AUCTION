-- Migration: Add All New Features
-- Date: 2024-11-25
-- Description: Database schema changes for 23 new features

-- ============================================
-- FEATURE 1: RTM Cards
-- ============================================
ALTER TABLE teams ADD COLUMN IF NOT EXISTS rtm_cards_remaining INTEGER DEFAULT 2;
ALTER TABLE players ADD COLUMN IF NOT EXISTS previous_team_id INTEGER;
ALTER TABLE auction_players ADD COLUMN IF NOT EXISTS is_rtm_eligible BOOLEAN DEFAULT FALSE;

-- ============================================
-- FEATURE 2: Accelerated Auction
-- ============================================
ALTER TABLE rooms ADD COLUMN IF NOT EXISTS is_accelerated_mode BOOLEAN DEFAULT FALSE;
ALTER TABLE auction_players ADD COLUMN IF NOT EXISTS is_accelerated BOOLEAN DEFAULT FALSE;
ALTER TABLE auction_players ADD COLUMN IF NOT EXISTS original_base_price DECIMAL(10,2);

-- ============================================
-- FEATURE 7: Auction History & Statistics
-- ============================================
CREATE TABLE IF NOT EXISTS auction_history (
    id SERIAL PRIMARY KEY,
    room_id INTEGER REFERENCES rooms(id) ON DELETE CASCADE,
    player_id INTEGER REFERENCES players(id),
    winning_team_id INTEGER REFERENCES teams(id),
    final_price DECIMAL(10,2) NOT NULL,
    base_price DECIMAL(10,2) NOT NULL,
    num_bids INTEGER DEFAULT 0,
    bid_duration INTEGER, -- seconds
    is_bargain BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_auction_history_room ON auction_history(room_id);
CREATE INDEX IF NOT EXISTS idx_auction_history_player ON auction_history(player_id);

-- ============================================
-- FEATURE 9: Trade Window
-- ============================================
CREATE TABLE IF NOT EXISTS trades (
    id SERIAL PRIMARY KEY,
    room_id INTEGER REFERENCES rooms(id) ON DELETE CASCADE,
    from_team_id INTEGER REFERENCES teams(id),
    to_team_id INTEGER REFERENCES teams(id),
    player_id INTEGER REFERENCES players(id),
    compensation DECIMAL(10,2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending', -- pending, accepted, rejected, cancelled
    proposed_by VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_trades_room ON trades(room_id);
CREATE INDEX IF NOT EXISTS idx_trades_status ON trades(status);

-- ============================================
-- FEATURE 10: Draft Mode
-- ============================================
CREATE TABLE IF NOT EXISTS draft_picks (
    id SERIAL PRIMARY KEY,
    room_id INTEGER REFERENCES rooms(id) ON DELETE CASCADE,
    team_id INTEGER REFERENCES teams(id),
    player_id INTEGER REFERENCES players(id),
    pick_number INTEGER NOT NULL,
    round_number INTEGER NOT NULL,
    pick_time INTEGER, -- seconds taken
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE rooms ADD COLUMN IF NOT EXISTS mode VARCHAR(20) DEFAULT 'auction'; -- auction, draft, silent
ALTER TABLE rooms ADD COLUMN IF NOT EXISTS draft_order JSONB; -- array of team_ids

CREATE INDEX IF NOT EXISTS idx_draft_picks_room ON draft_picks(room_id);

-- ============================================
-- FEATURE 13: Spectator Mode
-- ============================================
CREATE TABLE IF NOT EXISTS spectators (
    id SERIAL PRIMARY KEY,
    room_id INTEGER REFERENCES rooms(id) ON DELETE CASCADE,
    username VARCHAR(100) NOT NULL,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_spectators_room ON spectators(room_id);

-- ============================================
-- FEATURE 14: Tournament Mode
-- ============================================
CREATE TABLE IF NOT EXISTS tournaments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    created_by VARCHAR(100),
    status VARCHAR(20) DEFAULT 'setup', -- setup, active, completed
    tournament_type VARCHAR(20) DEFAULT 'bracket', -- bracket, league, knockout
    max_teams INTEGER DEFAULT 8,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);

ALTER TABLE rooms ADD COLUMN IF NOT EXISTS tournament_id INTEGER REFERENCES tournaments(id);
ALTER TABLE rooms ADD COLUMN IF NOT EXISTS tournament_round INTEGER;

CREATE TABLE IF NOT EXISTS tournament_standings (
    id SERIAL PRIMARY KEY,
    tournament_id INTEGER REFERENCES tournaments(id) ON DELETE CASCADE,
    team_id INTEGER REFERENCES teams(id),
    room_id INTEGER REFERENCES rooms(id),
    points INTEGER DEFAULT 0,
    rank INTEGER,
    total_spent DECIMAL(10,2),
    team_strength DECIMAL(5,2)
);

CREATE INDEX IF NOT EXISTS idx_tournament_standings ON tournament_standings(tournament_id, rank);

-- ============================================
-- FEATURE 15: Team Alliances
-- ============================================
CREATE TABLE IF NOT EXISTS alliances (
    id SERIAL PRIMARY KEY,
    room_id INTEGER REFERENCES rooms(id) ON DELETE CASCADE,
    name VARCHAR(100),
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS alliance_members (
    id SERIAL PRIMARY KEY,
    alliance_id INTEGER REFERENCES alliances(id) ON DELETE CASCADE,
    team_id INTEGER REFERENCES teams(id),
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS alliance_messages (
    id SERIAL PRIMARY KEY,
    alliance_id INTEGER REFERENCES alliances(id) ON DELETE CASCADE,
    username VARCHAR(100),
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- FEATURE 17: Custom Team Branding
-- ============================================
ALTER TABLE teams ADD COLUMN IF NOT EXISTS logo_url VARCHAR(500);
ALTER TABLE teams ADD COLUMN IF NOT EXISTS primary_color VARCHAR(7) DEFAULT '#1e40af';
ALTER TABLE teams ADD COLUMN IF NOT EXISTS secondary_color VARCHAR(7) DEFAULT '#3b82f6';
ALTER TABLE teams ADD COLUMN IF NOT EXISTS anthem_url VARCHAR(500);

-- ============================================
-- FEATURE 21 & 22: Notifications
-- ============================================
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    username VARCHAR(100),
    room_id INTEGER REFERENCES rooms(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL, -- bid_turn, budget_warning, player_recommendation, etc.
    title VARCHAR(200),
    message TEXT,
    data JSONB,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(username, is_read);
CREATE INDEX IF NOT EXISTS idx_notifications_created ON notifications(created_at);

CREATE TABLE IF NOT EXISTS notification_preferences (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE,
    email_notifications BOOLEAN DEFAULT TRUE,
    sms_notifications BOOLEAN DEFAULT FALSE,
    push_notifications BOOLEAN DEFAULT TRUE,
    email_address VARCHAR(255),
    phone_number VARCHAR(20)
);

-- ============================================
-- FEATURE 25: Achievement System
-- ============================================
CREATE TABLE IF NOT EXISTS achievements (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    icon VARCHAR(50),
    category VARCHAR(50), -- auction, team_building, strategy, social
    criteria JSONB,
    points INTEGER DEFAULT 0,
    rarity VARCHAR(20) DEFAULT 'common' -- common, rare, epic, legendary
);

CREATE TABLE IF NOT EXISTS user_achievements (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100),
    achievement_id INTEGER REFERENCES achievements(id),
    room_id INTEGER REFERENCES rooms(id),
    earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(username, achievement_id, room_id)
);

CREATE INDEX IF NOT EXISTS idx_user_achievements ON user_achievements(username);

-- ============================================
-- FEATURE 31 & 32: Export & Historical Data
-- ============================================
CREATE TABLE IF NOT EXISTS archived_auctions (
    id SERIAL PRIMARY KEY,
    room_code VARCHAR(10),
    room_data JSONB,
    teams_data JSONB,
    players_data JSONB,
    statistics JSONB,
    completed_at TIMESTAMP,
    archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_archived_auctions_code ON archived_auctions(room_code);
CREATE INDEX IF NOT EXISTS idx_archived_auctions_completed ON archived_auctions(completed_at);

-- ============================================
-- FEATURE 37: User Accounts
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    display_name VARCHAR(100),
    avatar_url VARCHAR(500),
    bio TEXT,
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    reset_token VARCHAR(255),
    reset_token_expires TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    total_auctions INTEGER DEFAULT 0,
    total_wins INTEGER DEFAULT 0,
    total_spent DECIMAL(12,2) DEFAULT 0,
    favorite_role VARCHAR(10),
    achievement_points INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    preferences JSONB
);

CREATE TABLE IF NOT EXISTS friendships (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    friend_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'pending', -- pending, accepted, blocked
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, friend_id)
);

CREATE INDEX IF NOT EXISTS idx_friendships_user ON friendships(user_id, status);

-- ============================================
-- FEATURE 39: Advanced Analytics
-- ============================================
CREATE TABLE IF NOT EXISTS analytics_events (
    id SERIAL PRIMARY KEY,
    room_id INTEGER REFERENCES rooms(id) ON DELETE CASCADE,
    username VARCHAR(100),
    event_type VARCHAR(50), -- bid_placed, player_won, rtm_used, etc.
    event_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_analytics_events_room ON analytics_events(room_id);
CREATE INDEX IF NOT EXISTS idx_analytics_events_type ON analytics_events(event_type);
CREATE INDEX IF NOT EXISTS idx_analytics_events_created ON analytics_events(created_at);

-- ============================================
-- Additional Enhancements
-- ============================================

-- Add theme preference
ALTER TABLE users ADD COLUMN IF NOT EXISTS theme VARCHAR(10) DEFAULT 'light';

-- Add player statistics tracking
ALTER TABLE players ADD COLUMN IF NOT EXISTS times_sold INTEGER DEFAULT 0;
ALTER TABLE players ADD COLUMN IF NOT EXISTS average_price DECIMAL(10,2);
ALTER TABLE players ADD COLUMN IF NOT EXISTS highest_price DECIMAL(10,2);

-- Add team performance metrics
ALTER TABLE teams ADD COLUMN IF NOT EXISTS batting_strength DECIMAL(5,2);
ALTER TABLE teams ADD COLUMN IF NOT EXISTS bowling_strength DECIMAL(5,2);
ALTER TABLE teams ADD COLUMN IF NOT EXISTS balance_score DECIMAL(5,2);

-- Add room settings
ALTER TABLE rooms ADD COLUMN IF NOT EXISTS settings JSONB DEFAULT '{}';
ALTER TABLE rooms ADD COLUMN IF NOT EXISTS allow_spectators BOOLEAN DEFAULT TRUE;
ALTER TABLE rooms ADD COLUMN IF NOT EXISTS is_private BOOLEAN DEFAULT FALSE;
ALTER TABLE rooms ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255);

-- ============================================
-- Insert Default Achievements
-- ============================================
INSERT INTO achievements (name, description, icon, category, criteria, points, rarity) VALUES
('First Blood', 'Win your first player in an auction', '🎯', 'auction', '{"type": "first_win"}', 10, 'common'),
('Bargain Hunter', 'Buy a player for 50% or less of their market value', '💰', 'auction', '{"type": "bargain", "threshold": 0.5}', 25, 'rare'),
('Big Spender', 'Spend 20 Cr or more on a single player', '💎', 'auction', '{"type": "high_bid", "amount": 20}', 20, 'rare'),
('Speed Demon', 'Win a bid in under 5 seconds', '⚡', 'auction', '{"type": "fast_win", "time": 5}', 15, 'common'),
('Comeback King', 'Win a player after being outbid 5 or more times', '👑', 'auction', '{"type": "comeback", "outbids": 5}', 30, 'epic'),
('Balanced Team', 'Build a team with perfect role distribution', '⚖️', 'team_building', '{"type": "balanced"}', 50, 'epic'),
('Dream Team', 'Build a team with average overall score above 80', '🌟', 'team_building', '{"type": "high_quality", "score": 80}', 75, 'legendary'),
('RTM Master', 'Successfully use all RTM cards', '🎴', 'strategy', '{"type": "rtm_usage"}', 40, 'rare'),
('Trade Mogul', 'Complete 5 successful trades', '🤝', 'strategy', '{"type": "trades", "count": 5}', 35, 'rare'),
('Social Butterfly', 'Form an alliance with 3 or more teams', '🦋', 'social', '{"type": "alliance", "members": 3}', 20, 'common'),
('Tournament Champion', 'Win a tournament', '🏆', 'tournament', '{"type": "tournament_win"}', 100, 'legendary'),
('Auction Master', 'Complete 10 auctions', '🎓', 'auction', '{"type": "auctions_completed", "count": 10}', 50, 'epic')
ON CONFLICT (name) DO NOTHING;

-- ============================================
-- Create Views for Analytics
-- ============================================

CREATE OR REPLACE VIEW team_statistics AS
SELECT 
    t.id,
    t.team_name,
    t.room_id,
    t.initial_purse - t.purse_left as total_spent,
    COUNT(tp.player_id) as total_players,
    AVG(p.overall_score) as avg_player_score,
    t.batting_strength,
    t.bowling_strength,
    t.balance_score
FROM teams t
LEFT JOIN team_players tp ON t.id = tp.team_id
LEFT JOIN players p ON tp.player_id = p.id
GROUP BY t.id;

CREATE OR REPLACE VIEW auction_statistics AS
SELECT 
    r.id as room_id,
    r.code as room_code,
    COUNT(DISTINCT ah.player_id) as total_players_sold,
    AVG(ah.final_price) as avg_sale_price,
    MAX(ah.final_price) as highest_sale,
    MIN(ah.final_price) as lowest_sale,
    AVG(ah.num_bids) as avg_bids_per_player,
    COUNT(CASE WHEN ah.is_bargain THEN 1 END) as total_bargains
FROM rooms r
LEFT JOIN auction_history ah ON r.id = ah.room_id
GROUP BY r.id, r.code;

-- ============================================
-- Triggers for automatic updates
-- ============================================

-- Update team strength when players are added
CREATE OR REPLACE FUNCTION update_team_strength()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE teams SET
        batting_strength = (
            SELECT AVG(p.batting_score)
            FROM team_players tp
            JOIN players p ON tp.player_id = p.id
            WHERE tp.team_id = NEW.team_id
        ),
        bowling_strength = (
            SELECT AVG(p.bowling_score)
            FROM team_players tp
            JOIN players p ON tp.player_id = p.id
            WHERE tp.team_id = NEW.team_id
        )
    WHERE id = NEW.team_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_team_strength
AFTER INSERT OR UPDATE ON team_players
FOR EACH ROW
EXECUTE FUNCTION update_team_strength();

-- Update player statistics
CREATE OR REPLACE FUNCTION update_player_stats()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE players SET
        times_sold = times_sold + 1,
        average_price = (
            SELECT AVG(final_price)
            FROM auction_history
            WHERE player_id = NEW.player_id
        ),
        highest_price = GREATEST(COALESCE(highest_price, 0), NEW.final_price)
    WHERE id = NEW.player_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_player_stats
AFTER INSERT ON auction_history
FOR EACH ROW
EXECUTE FUNCTION update_player_stats();

-- ============================================
-- Indexes for Performance
-- ============================================

CREATE INDEX IF NOT EXISTS idx_teams_room ON teams(room_id);
CREATE INDEX IF NOT EXISTS idx_team_players_team ON team_players(team_id);
CREATE INDEX IF NOT EXISTS idx_team_players_player ON team_players(player_id);
CREATE INDEX IF NOT EXISTS idx_auction_players_room ON auction_players(room_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- ============================================
-- Migration Complete
-- ============================================
