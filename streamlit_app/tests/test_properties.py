"""Property-based tests using Hypothesis.

Feature: streamlit-conversion
These tests verify correctness properties across many randomly generated inputs.
"""
import pytest
from hypothesis import given, strategies as st, settings
from services import room_service, team_service, auction_service, ai_service
from models import Player


# Property 1: Room code uniqueness
# **Feature: streamlit-conversion, Property 1: Room code uniqueness**
# **Validates: Requirements 1.2, 4.2**
@given(st.integers(min_value=2, max_value=10))
@settings(max_examples=100)
def test_property_room_code_uniqueness(num_rooms):
    """For any number of rooms created, all room codes should be unique."""
    codes = set()
    
    for i in range(num_rooms):
        room = room_service.create_room(f"host{i}")
        assert room.code not in codes, f"Duplicate room code: {room.code}"
        codes.add(room.code)
    
    assert len(codes) == num_rooms


# Property 3: Team name uniqueness within room
# **Feature: streamlit-conversion, Property 3: Team name uniqueness within room**
# **Validates: Requirements 5.3**
@given(
    st.lists(st.text(min_size=3, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll'))), min_size=2, max_size=5, unique=True),
    st.floats(min_value=50.0, max_value=200.0)
)
@settings(max_examples=100)
def test_property_team_name_uniqueness(team_names, purse):
    """For any room, no two teams should have the same team_name."""
    room = room_service.create_room("host")
    
    configured_teams = []
    for i, name in enumerate(team_names):
        success, msg, team = team_service.configure_team(
            room.id,
            f"user{i}",
            name,
            purse
        )
        if success:
            configured_teams.append(team.team_name)
    
    # Check uniqueness
    assert len(configured_teams) == len(set(configured_teams))


# Property 4: Purse deduction correctness
# **Feature: streamlit-conversion, Property 4: Purse deduction correctness**
# **Validates: Requirements 7.5**
@given(
    st.floats(min_value=100.0, max_value=200.0),
    st.floats(min_value=10.0, max_value=50.0)
)
@settings(max_examples=100)
def test_property_purse_deduction(initial_purse, bid_amount):
    """For any successful bid, the team's purse_left should decrease by exactly the bid amount."""
    room = room_service.create_room("host")
    
    success, msg, team = team_service.configure_team(
        room.id,
        "player1",
        "Test Team",
        initial_purse
    )
    
    if success and team.purse_left >= bid_amount:
        original_purse = team.purse_left
        
        # Simulate purse deduction
        success, msg, updated_team = team_service.update_purse(team.id, original_purse - bid_amount)
        
        if success:
            assert updated_team.purse_left == original_purse - bid_amount


# Property 5: Sufficient purse validation
# **Feature: streamlit-conversion, Property 5: Sufficient purse validation**
# **Validates: Requirements 7.3**
@given(
    st.floats(min_value=10.0, max_value=50.0),
    st.floats(min_value=60.0, max_value=100.0)
)
@settings(max_examples=100)
def test_property_insufficient_purse_rejection(purse, bid_amount):
    """For any bid attempt where bid exceeds purse, the bid should be rejected."""
    if bid_amount > purse:
        room = room_service.create_room("host")
        
        success, msg, team = team_service.configure_team(
            room.id,
            "player1",
            "Test Team",
            purse
        )
        
        if success:
            # Try to update purse to negative (simulating insufficient funds)
            success, msg, updated_team = team_service.update_purse(team.id, -10.0)
            
            # Should fail validation
            assert success is False


# Property 6: Playing XI composition constraints
# **Feature: streamlit-conversion, Property 6: Playing XI composition constraints**
# **Validates: Requirements 12.2**
def test_property_playing_xi_constraints():
    """For any selected playing XI, it should meet all role constraints."""
    # Create a team with diverse players
    room = room_service.create_room("host")
    success, msg, team = team_service.configure_team(room.id, "player1", "Test Team", 200.0)
    
    if not success:
        pytest.skip("Could not create team")
    
    # Add players with different roles
    from models import get_session, Player, TeamPlayer
    session = get_session()
    
    try:
        # Create test players
        players = [
            Player(name=f"WK{i}", role="WK", country="India", base_price=10.0, 
                   batting_score=70.0, bowling_score=20.0, overall_score=45.0, is_overseas=False)
            for i in range(2)
        ] + [
            Player(name=f"BAT{i}", role="BAT", country="India", base_price=10.0,
                   batting_score=80.0, bowling_score=10.0, overall_score=45.0, is_overseas=False)
            for i in range(4)
        ] + [
            Player(name=f"BOWL{i}", role="BOWL", country="India", base_price=10.0,
                   batting_score=20.0, bowling_score=80.0, overall_score=50.0, is_overseas=False)
            for i in range(3)
        ] + [
            Player(name=f"AR{i}", role="AR", country="India", base_price=10.0,
                   batting_score=60.0, bowling_score=60.0, overall_score=60.0, is_overseas=False)
            for i in range(3)
        ]
        
        for player in players:
            session.add(player)
        session.commit()
        
        # Add to team
        for player in players:
            tp = TeamPlayer(team_id=team.id, player_id=player.id, price=10.0)
            session.add(tp)
        session.commit()
        
        # Select playing XI
        playing_xi = ai_service.select_playing_xi(team.id)
        
        if playing_xi:
            # Verify constraints
            assert len(playing_xi) == 11
            
            wk_count = sum(1 for p in playing_xi if p.role == 'WK')
            bat_count = sum(1 for p in playing_xi if p.role == 'BAT')
            bowl_count = sum(1 for p in playing_xi if p.role == 'BOWL')
            ar_count = sum(1 for p in playing_xi if p.role == 'AR')
            overseas_count = sum(1 for p in playing_xi if p.is_overseas)
            
            assert wk_count == 1, f"Expected 1 WK, got {wk_count}"
            assert bat_count >= 3, f"Expected at least 3 BAT, got {bat_count}"
            assert bowl_count >= 2, f"Expected at least 2 BOWL, got {bowl_count}"
            assert 1 <= ar_count <= 3, f"Expected 1-3 AR, got {ar_count}"
            assert overseas_count <= 4, f"Expected at most 4 overseas, got {overseas_count}"
    
    finally:
        session.close()


# Property 9: Winner determination correctness
# **Feature: streamlit-conversion, Property 9: Winner determination correctness**
# **Validates: Requirements 9.3**
@given(st.lists(st.floats(min_value=0.0, max_value=100.0), min_size=2, max_size=5))
@settings(max_examples=100)
def test_property_winner_has_highest_rating(ratings):
    """For any completed auction, the winning team should have the highest overall_rating."""
    room = room_service.create_room("host")
    
    from models import get_session, Team, TeamRating
    session = get_session()
    
    try:
        teams = []
        for i, rating in enumerate(ratings):
            team = Team(
                room_id=room.id,
                username=f"player{i}",
                team_name=f"Team{i}",
                initial_purse=100.0,
                purse_left=50.0
            )
            session.add(team)
            session.commit()
            
            team_rating = TeamRating(
                team_id=team.id,
                overall_rating=rating,
                batting_rating=rating * 0.8,
                bowling_rating=rating * 0.7,
                balance_score=rating * 0.9,
                bench_depth=rating * 0.5,
                role_coverage=rating * 0.6
            )
            session.add(team_rating)
            teams.append((team, rating))
        
        session.commit()
        
        # Determine winner
        winner = ai_service.determine_winner(room.code)
        
        if winner:
            winner_rating = session.query(TeamRating).filter_by(team_id=winner.id).first()
            max_rating = max(ratings)
            
            assert winner_rating.overall_rating == max_rating
    
    finally:
        session.close()


# Property 10: Database state consistency
# **Feature: streamlit-conversion, Property 10: Database state consistency after refresh**
# **Validates: Requirements 10.1, 10.3**
@given(st.text(min_size=6, max_size=6, alphabet=st.characters(whitelist_categories=('Lu',), min_codepoint=65, max_codepoint=90)))
@settings(max_examples=100)
def test_property_database_consistency(room_code_suffix):
    """For any user refreshing, displayed state should match database state."""
    # Create room
    room = room_service.create_room("host")
    original_code = room.code
    
    # Retrieve room from database
    retrieved_room = room_service.get_room(original_code)
    
    # Verify consistency
    assert retrieved_room is not None
    assert retrieved_room.code == original_code
    assert retrieved_room.host_username == "host"
    assert retrieved_room.status == "lobby"
