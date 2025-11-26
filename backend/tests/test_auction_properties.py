"""Property-based tests for Auction engine."""
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from app.models import Room, Player, AuctionPlayer
from app.services.auction_service import present_next_player, initialize_auction
from app.services.room_service import create_room
from app import db
import string


# Feature: ipl-mock-auction-arena, Property 16: Player presentation data completeness
# Validates: Requirements 7.1, 7.2
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
@given(
    host_username=st.text(alphabet=string.ascii_letters + string.digits, min_size=1, max_size=100)
)
def test_player_presentation_data_completeness(app, db_session, host_username):
    """
    Property 16: Player presentation data completeness
    For any player presented for auction, the display data should include name, role, 
    country, base price, statistics, and overall rating.
    """
    with app.app_context():
        # Create a room
        room = create_room(host_username)
        room_code = room.code
        
        # Create a test player
        player = Player(
            name="Test Player",
            role="BAT",
            country="India",
            base_price=10.0,
            batting_score=50.0,
            bowling_score=30.0,
            overall_score=40.0,
            is_overseas=False
        )
        db_session.add(player)
        db_session.commit()
        
        # Initialize auction
        initialize_auction(room_code)
        
        # Present next player
        presented_player = present_next_player(room_code)
        
        # Verify player data completeness
        assert presented_player is not None, "Player should be presented"
        assert presented_player.name is not None and presented_player.name != "", \
            "Player name should be present"
        assert presented_player.role is not None and presented_player.role != "", \
            "Player role should be present"
        assert presented_player.country is not None and presented_player.country != "", \
            "Player country should be present"
        assert presented_player.base_price is not None and presented_player.base_price > 0, \
            "Player base price should be present and positive"
        assert presented_player.batting_score is not None, \
            "Player batting score should be present"
        assert presented_player.bowling_score is not None, \
            "Player bowling score should be present"
        assert presented_player.overall_score is not None, \
            "Player overall score should be present"
        
        # Clean up
        auction_players = AuctionPlayer.query.filter_by(room_id=room.id).all()
        for ap in auction_players:
            db_session.delete(ap)
        db_session.delete(player)
        db_session.delete(room)
        db_session.commit()


# Feature: ipl-mock-auction-arena, Property 17: Timer initialization on player presentation
# Validates: Requirements 7.3
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
@given(
    host_username=st.text(alphabet=string.ascii_letters + string.digits, min_size=1, max_size=100)
)
def test_timer_initialization(app, db_session, host_username):
    """
    Property 17: Timer initialization on player presentation
    For any player presented for auction, a 30-second countdown timer should be started.
    """
    with app.app_context():
        from app.services.auction_service import get_current_auction_state
        
        # Create a room
        room = create_room(host_username)
        room_code = room.code
        
        # Create a test player
        player = Player(
            name="Test Player",
            role="BAT",
            country="India",
            base_price=10.0,
            batting_score=50.0,
            bowling_score=30.0,
            overall_score=40.0,
            is_overseas=False
        )
        db_session.add(player)
        db_session.commit()
        
        # Initialize auction
        initialize_auction(room_code)
        
        # Present next player
        presented_player = present_next_player(room_code)
        assert presented_player is not None, "Player should be presented"
        
        # Get auction state
        state = get_current_auction_state(room_code)
        
        # Verify timer is initialized to 30 seconds
        assert state.timer_remaining == 30, \
            f"Timer should be initialized to 30 seconds, got {state.timer_remaining}"
        
        # Clean up
        auction_players = AuctionPlayer.query.filter_by(room_id=room.id).all()
        for ap in auction_players:
            db_session.delete(ap)
        db_session.delete(player)
        db_session.delete(room)
        db_session.commit()


# Feature: ipl-mock-auction-arena, Property 18: Bid increment consistency
# Validates: Requirements 8.1
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
@given(
    host_username=st.text(alphabet=string.ascii_letters + string.digits, min_size=1, max_size=100),
    team_name=st.text(alphabet=string.ascii_letters + string.digits, min_size=1, max_size=100),
    initial_purse=st.floats(min_value=1000.0, max_value=10000.0)
)
def test_bid_increment_consistency(app, db_session, host_username, team_name, initial_purse):
    """
    Property 18: Bid increment consistency
    For any current bid amount, placing a bid should increase it by exactly 
    the configured bid increment.
    """
    with app.app_context():
        from app.services.team_service import configure_team
        from app.services.auction_service import place_bid
        
        # Create a room
        room = create_room(host_username)
        room_code = room.code
        
        # Configure team
        success, message, team = configure_team(room.id, host_username, team_name, initial_purse)
        assert success is True, f"Team configuration should succeed: {message}"
        
        # Create a test player
        player = Player(
            name="Test Player",
            role="BAT",
            country="India",
            base_price=10.0,
            batting_score=50.0,
            bowling_score=30.0,
            overall_score=40.0,
            is_overseas=False
        )
        db_session.add(player)
        db_session.commit()
        
        # Initialize auction
        initialize_auction(room_code)
        
        # Present next player
        presented_player = present_next_player(room_code)
        assert presented_player is not None, "Player should be presented"
        
        # Get initial bid (base price)
        from app.services.auction_service import _auction_states
        initial_bid = _auction_states[room_code]['current_bid']
        bid_increment = _auction_states[room_code]['bid_increment']
        
        # Place a bid
        result = place_bid(room_code, host_username)
        
        # Verify bid increment
        if result.success:
            expected_bid = initial_bid + bid_increment
            assert result.new_bid == expected_bid, \
                f"New bid should be {expected_bid}, got {result.new_bid}"
        
        # Clean up
        auction_players = AuctionPlayer.query.filter_by(room_id=room.id).all()
        for ap in auction_players:
            db_session.delete(ap)
        db_session.delete(player)
        db_session.delete(team)
        db_session.delete(room)
        db_session.commit()


# Feature: ipl-mock-auction-arena, Property 19: Purse sufficiency check
# Validates: Requirements 8.2
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
@given(
    host_username=st.text(alphabet=string.ascii_letters + string.digits, min_size=1, max_size=100),
    team_name=st.text(alphabet=string.ascii_letters + string.digits, min_size=1, max_size=100),
    initial_purse=st.floats(min_value=10.0, max_value=50.0)  # Low purse to test insufficiency
)
def test_purse_sufficiency_check(app, db_session, host_username, team_name, initial_purse):
    """
    Property 19: Purse sufficiency check
    For any bid attempt, if the user's remaining purse is less than the bid amount, 
    the bid should be rejected.
    """
    with app.app_context():
        from app.services.team_service import configure_team
        from app.services.auction_service import place_bid
        
        # Create a room
        room = create_room(host_username)
        room_code = room.code
        
        # Configure team with low purse
        success, message, team = configure_team(room.id, host_username, team_name, initial_purse)
        assert success is True, f"Team configuration should succeed: {message}"
        
        # Create a test player with high base price
        player = Player(
            name="Expensive Player",
            role="BAT",
            country="India",
            base_price=100.0,  # High base price
            batting_score=90.0,
            bowling_score=80.0,
            overall_score=85.0,
            is_overseas=False
        )
        db_session.add(player)
        db_session.commit()
        
        # Initialize auction
        initialize_auction(room_code)
        
        # Present next player
        presented_player = present_next_player(room_code)
        assert presented_player is not None, "Player should be presented"
        
        # Get current bid and calculate what the new bid would be
        from app.services.auction_service import _auction_states
        current_bid = _auction_states[room_code]['current_bid']
        bid_increment = _auction_states[room_code]['bid_increment']
        new_bid = current_bid + bid_increment
        
        # If new bid exceeds purse, bid should be rejected
        if new_bid > team.purse_left:
            result = place_bid(room_code, host_username)
            assert result.success is False, \
                "Bid should be rejected when purse is insufficient"
            assert "Insufficient purse" in result.message, \
                f"Error message should mention insufficient purse, got: {result.message}"
            
            # Verify bid didn't change
            assert _auction_states[room_code]['current_bid'] == current_bid, \
                "Current bid should not change when bid is rejected"
        
        # Clean up
        auction_players = AuctionPlayer.query.filter_by(room_id=room.id).all()
        for ap in auction_players:
            db_session.delete(ap)
        db_session.delete(player)
        db_session.delete(team)
        db_session.delete(room)
        db_session.commit()



# Feature: ipl-mock-auction-arena, Property 21: Player assignment on timer expiry
# Validates: Requirements 8.5
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
@given(
    host_username=st.text(alphabet=string.ascii_letters + string.digits, min_size=1, max_size=100),
    team_name=st.text(alphabet=string.ascii_letters + string.digits, min_size=1, max_size=100),
    initial_purse=st.floats(min_value=1000.0, max_value=10000.0)
)
def test_player_assignment_on_timer_expiry(app, db_session, host_username, team_name, initial_purse):
    """
    Property 21: Player assignment on timer expiry
    For any auction timer that reaches zero, the player should be assigned to 
    the team with the highest bid.
    """
    with app.app_context():
        from app.services.team_service import configure_team
        from app.services.auction_service import place_bid, handle_timer_expiry
        from app.models.team_player import TeamPlayer
        
        # Create a room
        room = create_room(host_username)
        room_code = room.code
        
        # Configure team
        success, message, team = configure_team(room.id, host_username, team_name, initial_purse)
        assert success is True, f"Team configuration should succeed: {message}"
        
        # Create a test player
        player = Player(
            name="Test Player",
            role="BAT",
            country="India",
            base_price=10.0,
            batting_score=50.0,
            bowling_score=30.0,
            overall_score=40.0,
            is_overseas=False
        )
        db_session.add(player)
        db_session.commit()
        
        # Initialize auction
        initialize_auction(room_code)
        
        # Present next player
        presented_player = present_next_player(room_code)
        assert presented_player is not None, "Player should be presented"
        
        # Place a bid
        result = place_bid(room_code, host_username)
        assert result.success is True, "Bid should be placed successfully"
        
        # Simulate timer expiry
        sold_info = handle_timer_expiry(room_code)
        
        # Verify player was assigned to the highest bidder
        assert sold_info is not None, "Timer expiry should return sold info"
        assert sold_info['sold_to'] == host_username, \
            f"Player should be assigned to {host_username}, got {sold_info['sold_to']}"
        assert sold_info['player'].id == player.id, \
            "Correct player should be assigned"
        
        # Verify auction player record is updated
        auction_player = AuctionPlayer.query.filter_by(
            room_id=room.id,
            player_id=player.id
        ).first()
        assert auction_player.is_sold is True, "Player should be marked as sold"
        assert auction_player.sold_to_team_id == team.id, \
            "Player should be assigned to correct team"
        
        # Verify team player record was created
        team_player = TeamPlayer.query.filter_by(
            team_id=team.id,
            player_id=player.id
        ).first()
        assert team_player is not None, "Team player record should be created"
        
        # Clean up
        if team_player:
            db_session.delete(team_player)
        auction_players = AuctionPlayer.query.filter_by(room_id=room.id).all()
        for ap in auction_players:
            db_session.delete(ap)
        db_session.delete(player)
        db_session.delete(team)
        db_session.delete(room)
        db_session.commit()



# Feature: ipl-mock-auction-arena, Property 23: Sale record persistence
# Validates: Requirements 9.2
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
@given(
    host_username=st.text(alphabet=string.ascii_letters + string.digits, min_size=1, max_size=100),
    team_name=st.text(alphabet=string.ascii_letters + string.digits, min_size=1, max_size=100),
    initial_purse=st.floats(min_value=1000.0, max_value=10000.0)
)
def test_sale_record_persistence(app, db_session, host_username, team_name, initial_purse):
    """
    Property 23: Sale record persistence
    For any sold player, the database should contain a record with the sold price 
    and winning team identifier.
    """
    with app.app_context():
        from app.services.team_service import configure_team
        from app.services.auction_service import place_bid, handle_timer_expiry
        from app.models.team_player import TeamPlayer
        
        # Create a room
        room = create_room(host_username)
        room_code = room.code
        
        # Configure team
        success, message, team = configure_team(room.id, host_username, team_name, initial_purse)
        assert success is True, f"Team configuration should succeed: {message}"
        
        # Create a test player
        player = Player(
            name="Test Player",
            role="BAT",
            country="India",
            base_price=10.0,
            batting_score=50.0,
            bowling_score=30.0,
            overall_score=40.0,
            is_overseas=False
        )
        db_session.add(player)
        db_session.commit()
        
        # Initialize auction
        initialize_auction(room_code)
        
        # Present next player
        presented_player = present_next_player(room_code)
        assert presented_player is not None, "Player should be presented"
        
        # Place a bid
        result = place_bid(room_code, host_username)
        assert result.success is True, "Bid should be placed successfully"
        sold_price = result.new_bid
        
        # Simulate timer expiry
        sold_info = handle_timer_expiry(room_code)
        assert sold_info is not None, "Timer expiry should return sold info"
        
        # Verify sale record in AuctionPlayer table
        auction_player = AuctionPlayer.query.filter_by(
            room_id=room.id,
            player_id=player.id
        ).first()
        
        assert auction_player is not None, "Auction player record should exist"
        assert auction_player.is_sold is True, "Player should be marked as sold"
        assert auction_player.sold_price == sold_price, \
            f"Sold price should be {sold_price}, got {auction_player.sold_price}"
        assert auction_player.sold_to_team_id == team.id, \
            f"Sold to team should be {team.id}, got {auction_player.sold_to_team_id}"
        assert auction_player.sold_at is not None, \
            "Sold timestamp should be recorded"
        
        # Clean up
        team_player = TeamPlayer.query.filter_by(team_id=team.id, player_id=player.id).first()
        if team_player:
            db_session.delete(team_player)
        auction_players = AuctionPlayer.query.filter_by(room_id=room.id).all()
        for ap in auction_players:
            db_session.delete(ap)
        db_session.delete(player)
        db_session.delete(team)
        db_session.delete(room)
        db_session.commit()



# Feature: ipl-mock-auction-arena, Property 24: Team player record creation
# Validates: Requirements 9.3
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
@given(
    host_username=st.text(alphabet=string.ascii_letters + string.digits, min_size=1, max_size=100),
    team_name=st.text(alphabet=string.ascii_letters + string.digits, min_size=1, max_size=100),
    initial_purse=st.floats(min_value=1000.0, max_value=10000.0)
)
def test_team_player_record_creation(app, db_session, host_username, team_name, initial_purse):
    """
    Property 24: Team player record creation
    For any player assigned to a team, a corresponding record should exist in 
    the team_players table.
    """
    with app.app_context():
        from app.services.team_service import configure_team
        from app.services.auction_service import place_bid, handle_timer_expiry
        from app.models.team_player import TeamPlayer
        
        # Create a room
        room = create_room(host_username)
        room_code = room.code
        
        # Configure team
        success, message, team = configure_team(room.id, host_username, team_name, initial_purse)
        assert success is True, f"Team configuration should succeed: {message}"
        
        # Create a test player
        player = Player(
            name="Test Player",
            role="BAT",
            country="India",
            base_price=10.0,
            batting_score=50.0,
            bowling_score=30.0,
            overall_score=40.0,
            is_overseas=False
        )
        db_session.add(player)
        db_session.commit()
        
        # Initialize auction
        initialize_auction(room_code)
        
        # Present next player
        presented_player = present_next_player(room_code)
        assert presented_player is not None, "Player should be presented"
        
        # Place a bid
        result = place_bid(room_code, host_username)
        assert result.success is True, "Bid should be placed successfully"
        sold_price = result.new_bid
        
        # Simulate timer expiry (assigns player to team)
        sold_info = handle_timer_expiry(room_code)
        assert sold_info is not None, "Timer expiry should return sold info"
        
        # Verify team player record was created
        team_player = TeamPlayer.query.filter_by(
            team_id=team.id,
            player_id=player.id
        ).first()
        
        assert team_player is not None, \
            "Team player record should exist in database"
        assert team_player.team_id == team.id, \
            f"Team player should belong to team {team.id}, got {team_player.team_id}"
        assert team_player.player_id == player.id, \
            f"Team player should reference player {player.id}, got {team_player.player_id}"
        assert team_player.price == sold_price, \
            f"Team player price should be {sold_price}, got {team_player.price}"
        assert team_player.in_playing_xi is False, \
            "Newly acquired player should not be in playing XI yet"
        assert team_player.is_impact_player is False, \
            "Newly acquired player should not be impact player yet"
        
        # Clean up
        if team_player:
            db_session.delete(team_player)
        auction_players = AuctionPlayer.query.filter_by(room_id=room.id).all()
        for ap in auction_players:
            db_session.delete(ap)
        db_session.delete(player)
        db_session.delete(team)
        db_session.delete(room)
        db_session.commit()
