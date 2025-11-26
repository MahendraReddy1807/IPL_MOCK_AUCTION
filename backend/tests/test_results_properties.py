"""Property-based tests for results endpoint."""
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from app.models import Team, Room, Player, TeamPlayer, TeamRating
from app import db
import string


# Custom strategy for generating players
@st.composite
def player_strategy(draw, role=None, is_overseas=None):
    """Generate a player with optional role and overseas constraints."""
    roles = ['BAT', 'BOWL', 'AR', 'WK']
    
    if role is None:
        role = draw(st.sampled_from(roles))
    
    if is_overseas is None:
        is_overseas = draw(st.booleans())
    
    player = Player(
        name=draw(st.text(alphabet=string.ascii_letters + ' ', min_size=3, max_size=30)),
        role=role,
        country=draw(st.sampled_from(['India', 'Australia', 'England', 'South Africa', 'New Zealand'])),
        base_price=draw(st.floats(min_value=1.0, max_value=100.0)),
        batting_score=draw(st.floats(min_value=0.0, max_value=100.0)),
        bowling_score=draw(st.floats(min_value=0.0, max_value=100.0)),
        overall_score=draw(st.floats(min_value=0.0, max_value=100.0)),
        is_overseas=is_overseas
    )
    return player


@st.composite
def team_with_complete_data_strategy(draw):
    """Generate a team with complete auction data including players and ratings."""
    num_players = draw(st.integers(min_value=11, max_value=20))
    num_playing_xi = 11
    
    # Generate players
    players = []
    for _ in range(num_players):
        players.append(draw(player_strategy()))
    
    # Select which players are in playing XI (first 11)
    playing_xi_indices = list(range(num_playing_xi))
    
    # Select impact player (one from bench)
    impact_player_index = None
    if num_players > num_playing_xi:
        impact_player_index = draw(st.integers(min_value=num_playing_xi, max_value=num_players - 1))
    
    return {
        'players': players,
        'playing_xi_indices': playing_xi_indices,
        'impact_player_index': impact_player_index
    }


# Feature: ipl-mock-auction-arena, Property 38: Results data completeness
# Validates: Requirements 15.1, 15.2, 15.3, 15.4, 15.5
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
@given(
    host_username=st.text(alphabet=string.ascii_letters + string.digits, min_size=1, max_size=50),
    team_name=st.text(alphabet=string.ascii_letters + string.digits + ' ', min_size=1, max_size=50),
    logo_url=st.text(alphabet=string.ascii_letters + string.digits + '/.', min_size=5, max_size=50),
    team_data=team_with_complete_data_strategy()
)
def test_results_data_completeness(client, app, db_session, host_username, team_name, logo_url, team_data):
    """
    Property 38: Results data completeness
    For any completed auction, the results should include each team's name, logo, 
    full squad, playing XI, impact player, and team rating.
    """
    with app.app_context():
        import uuid
        import json
        
        # Create room with unique code
        room_code = f"TEST{uuid.uuid4().hex[:8].upper()}"
        room = Room(
            code=room_code,
            host_username=host_username,
            status='completed'
        )
        db_session.add(room)
        db_session.commit()
        
        # Create team
        team = Team(
            room_id=room.id,
            username=host_username,
            team_name=team_name,
            logo_url=logo_url,
            initial_purse=1000.0,
            purse_left=500.0
        )
        db_session.add(team)
        db_session.commit()
        
        # Add players to database and team
        players = team_data['players']
        playing_xi_indices = team_data['playing_xi_indices']
        impact_player_index = team_data['impact_player_index']
        
        for i, player in enumerate(players):
            db_session.add(player)
            db_session.commit()
            
            is_in_playing_xi = i in playing_xi_indices
            is_impact = i == impact_player_index
            
            team_player = TeamPlayer(
                team_id=team.id,
                player_id=player.id,
                price=10.0,
                in_playing_xi=is_in_playing_xi,
                is_impact_player=is_impact
            )
            db_session.add(team_player)
        
        db_session.commit()
        
        # Add team rating
        team_rating = TeamRating(
            team_id=team.id,
            overall_rating=85.5,
            batting_rating=80.0,
            bowling_rating=75.0,
            balance_score=70.0,
            bench_depth=65.0,
            role_coverage=90.0
        )
        db_session.add(team_rating)
        db_session.commit()
        
        # Call the results API endpoint
        response = client.get(f'/api/results/{room_code}')
        
        # Verify response is successful
        assert response.status_code == 200, \
            f"Results endpoint should return 200, got {response.status_code}"
        
        data = json.loads(response.data)
        
        # Verify room code is present
        assert 'room_code' in data, "Results should include room_code"
        assert data['room_code'] == room_code, "Room code should match"
        
        # Verify teams data is present
        assert 'teams' in data, "Results should include teams"
        assert len(data['teams']) > 0, "Results should have at least one team"
        
        team_result = data['teams'][0]
        
        # Requirement 15.1: Display each team's name and logo
        assert 'team_name' in team_result, "Team result should include team_name"
        assert team_result['team_name'] == team_name, "Team name should match"
        assert 'logo_url' in team_result, "Team result should include logo_url"
        assert team_result['logo_url'] == logo_url, "Logo URL should match"
        
        # Requirement 15.2: Show each team's full squad with player names and roles
        assert 'squad' in team_result, "Team result should include squad"
        assert len(team_result['squad']) == len(players), \
            f"Squad should have {len(players)} players, got {len(team_result['squad'])}"
        
        for player_data in team_result['squad']:
            assert 'name' in player_data, "Squad player should have name"
            assert 'role' in player_data, "Squad player should have role"
            assert 'id' in player_data, "Squad player should have id"
            assert 'country' in player_data, "Squad player should have country"
            assert 'overall_score' in player_data, "Squad player should have overall_score"
            assert 'price' in player_data, "Squad player should have price"
        
        # Requirement 15.3: Highlight the playing XI for each team
        assert 'playing_xi' in team_result, "Team result should include playing_xi"
        assert len(team_result['playing_xi']) == len(playing_xi_indices), \
            f"Playing XI should have {len(playing_xi_indices)} players"
        
        for player_data in team_result['playing_xi']:
            assert 'name' in player_data, "Playing XI player should have name"
            assert 'role' in player_data, "Playing XI player should have role"
        
        # Requirement 15.4: Display the impact player for each team
        assert 'impact_player' in team_result, "Team result should include impact_player"
        
        if impact_player_index is not None:
            assert team_result['impact_player'] is not None, \
                "Impact player should be present when one is selected"
            assert 'name' in team_result['impact_player'], \
                "Impact player should have name"
            assert 'role' in team_result['impact_player'], \
                "Impact player should have role"
        
        # Requirement 15.5: Display the team rating for each team
        assert 'rating' in team_result, "Team result should include rating"
        assert team_result['rating'] is not None, "Rating should not be None"
        
        rating = team_result['rating']
        assert 'overall_rating' in rating, "Rating should include overall_rating"
        assert 'batting_rating' in rating, "Rating should include batting_rating"
        assert 'bowling_rating' in rating, "Rating should include bowling_rating"
        assert 'balance_score' in rating, "Rating should include balance_score"
        assert 'bench_depth' in rating, "Rating should include bench_depth"
        assert 'role_coverage' in rating, "Rating should include role_coverage"
        
        assert rating['overall_rating'] == 85.5, "Overall rating should match"
        assert rating['batting_rating'] == 80.0, "Batting rating should match"
        assert rating['bowling_rating'] == 75.0, "Bowling rating should match"
        
        # Clean up
        TeamRating.query.filter_by(team_id=team.id).delete()
        db_session.query(TeamPlayer).filter_by(team_id=team.id).delete()
        db_session.commit()
        for player in players:
            db_session.delete(player)
        db_session.delete(team)
        db_session.delete(room)
        db_session.commit()
