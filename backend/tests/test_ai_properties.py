"""Property-based tests for AI service."""
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck, assume
from app.models import Team, Room, Player, TeamPlayer
from app.services.ai_service import select_playing_xi, is_valid_combination
from app import db
import string


# Custom strategy for generating players with specific roles
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
def team_with_players_strategy(draw, min_players=11, max_players=15):
    """Generate a team with a squad of players."""
    num_players = draw(st.integers(min_value=min_players, max_value=max_players))
    
    # Ensure we have enough of each role to form a valid XI
    # We need: 1 WK, 3+ BAT, 2+ BOWL, 1-3 AR, max 4 overseas
    
    # Generate required minimum players
    players = []
    
    # 1 WK (Indian to be safe)
    players.append(draw(player_strategy(role='WK', is_overseas=False)))
    
    # 3 BAT (mix of Indian and overseas)
    for _ in range(3):
        players.append(draw(player_strategy(role='BAT')))
    
    # 2 BOWL (mix of Indian and overseas)
    for _ in range(2):
        players.append(draw(player_strategy(role='BOWL')))
    
    # 2 AR (to have between 1-3)
    for _ in range(2):
        players.append(draw(player_strategy(role='AR')))
    
    # Fill remaining slots with random roles
    remaining = num_players - len(players)
    for _ in range(remaining):
        players.append(draw(player_strategy()))
    
    return players


# Feature: ipl-mock-auction-arena, Property 28: Playing XI size constraint
# Validates: Requirements 11.1
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
@given(
    host_username=st.text(alphabet=string.ascii_letters + string.digits, min_size=1, max_size=50),
    team_name=st.text(alphabet=string.ascii_letters + string.digits + ' ', min_size=1, max_size=50),
    players=team_with_players_strategy(min_players=11, max_players=15)
)
def test_playing_xi_size_constraint(app, db_session, host_username, team_name, players):
    """
    Property 28: Playing XI size constraint
    For any team with at least 11 players, the selected playing XI should contain 
    exactly 11 players.
    """
    with app.app_context():
        import uuid
        # Create room with unique code
        room = Room(
            code=f"TEST{uuid.uuid4().hex[:8].upper()}",
            host_username=host_username
        )
        db_session.add(room)
        db_session.commit()
        
        # Create team
        team = Team(
            room_id=room.id,
            username=host_username,
            team_name=team_name,
            initial_purse=1000.0,
            purse_left=1000.0
        )
        db_session.add(team)
        db_session.commit()
        
        # Add players to database and team
        for player in players:
            db_session.add(player)
            db_session.commit()
            
            team_player = TeamPlayer(
                team_id=team.id,
                player_id=player.id,
                price=10.0
            )
            db_session.add(team_player)
        
        db_session.commit()
        
        # Select playing XI
        playing_xi = select_playing_xi(team.id)
        
        # Verify size constraint
        if len(players) >= 11:
            # Should return exactly 11 players if a valid combination exists
            if len(playing_xi) > 0:  # If a valid combination was found
                assert len(playing_xi) == 11, \
                    f"Playing XI should have exactly 11 players, got {len(playing_xi)}"
        
        # Clean up - delete in correct order to avoid foreign key issues
        db_session.query(TeamPlayer).filter_by(team_id=team.id).delete()
        db_session.commit()
        for player in players:
            db_session.delete(player)
        db_session.delete(team)
        db_session.delete(room)
        db_session.commit()



# Feature: ipl-mock-auction-arena, Property 29: Playing XI composition constraints
# Validates: Requirements 11.2, 11.3, 11.4, 11.5, 11.6
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
@given(
    host_username=st.text(alphabet=string.ascii_letters + string.digits, min_size=1, max_size=50),
    team_name=st.text(alphabet=string.ascii_letters + string.digits + ' ', min_size=1, max_size=50),
    players=team_with_players_strategy(min_players=11, max_players=15)
)
def test_playing_xi_composition_constraints(app, db_session, host_username, team_name, players):
    """
    Property 29: Playing XI composition constraints
    For any selected playing XI, it should contain exactly 1 wicket-keeper, 
    at least 3 batsmen, at least 2 bowlers, between 1 and 3 all-rounders, 
    and at most 4 overseas players.
    """
    with app.app_context():
        import uuid
        # Create room with unique code
        room = Room(
            code=f"TEST{uuid.uuid4().hex[:8].upper()}",
            host_username=host_username
        )
        db_session.add(room)
        db_session.commit()
        
        # Create team
        team = Team(
            room_id=room.id,
            username=host_username,
            team_name=team_name,
            initial_purse=1000.0,
            purse_left=1000.0
        )
        db_session.add(team)
        db_session.commit()
        
        # Add players to database and team
        for player in players:
            db_session.add(player)
            db_session.commit()
            
            team_player = TeamPlayer(
                team_id=team.id,
                player_id=player.id,
                price=10.0
            )
            db_session.add(team_player)
        
        db_session.commit()
        
        # Select playing XI
        playing_xi = select_playing_xi(team.id)
        
        # If a playing XI was selected, verify composition constraints
        if len(playing_xi) == 11:
            # Count by role
            wk_count = sum(1 for p in playing_xi if p.role == 'WK')
            bat_count = sum(1 for p in playing_xi if p.role == 'BAT')
            bowl_count = sum(1 for p in playing_xi if p.role == 'BOWL')
            ar_count = sum(1 for p in playing_xi if p.role == 'AR')
            overseas_count = sum(1 for p in playing_xi if p.is_overseas)
            
            # Verify constraints
            assert wk_count == 1, \
                f"Playing XI should have exactly 1 wicket-keeper, got {wk_count}"
            assert bat_count >= 3, \
                f"Playing XI should have at least 3 batsmen, got {bat_count}"
            assert bowl_count >= 2, \
                f"Playing XI should have at least 2 bowlers, got {bowl_count}"
            assert 1 <= ar_count <= 3, \
                f"Playing XI should have between 1 and 3 all-rounders, got {ar_count}"
            assert overseas_count <= 4, \
                f"Playing XI should have at most 4 overseas players, got {overseas_count}"
        
        # Clean up - delete in correct order to avoid foreign key issues
        db_session.query(TeamPlayer).filter_by(team_id=team.id).delete()
        db_session.commit()
        for player in players:
            db_session.delete(player)
        db_session.delete(team)
        db_session.delete(room)
        db_session.commit()



# Feature: ipl-mock-auction-arena, Property 30: Playing XI optimization
# Validates: Requirements 11.7
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
@given(
    host_username=st.text(alphabet=string.ascii_letters + string.digits, min_size=1, max_size=50),
    team_name=st.text(alphabet=string.ascii_letters + string.digits + ' ', min_size=1, max_size=50),
    players=team_with_players_strategy(min_players=11, max_players=14)
)
def test_playing_xi_optimization(app, db_session, host_username, team_name, players):
    """
    Property 30: Playing XI optimization
    For any team, the selected playing XI should be a valid combination with 
    the highest total overall score among all possible valid combinations.
    """
    with app.app_context():
        import uuid
        from itertools import combinations
        
        # Create room with unique code
        room = Room(
            code=f"TEST{uuid.uuid4().hex[:8].upper()}",
            host_username=host_username
        )
        db_session.add(room)
        db_session.commit()
        
        # Create team
        team = Team(
            room_id=room.id,
            username=host_username,
            team_name=team_name,
            initial_purse=1000.0,
            purse_left=1000.0
        )
        db_session.add(team)
        db_session.commit()
        
        # Add players to database and team
        for player in players:
            db_session.add(player)
            db_session.commit()
            
            team_player = TeamPlayer(
                team_id=team.id,
                player_id=player.id,
                price=10.0
            )
            db_session.add(team_player)
        
        db_session.commit()
        
        # Select playing XI
        playing_xi = select_playing_xi(team.id)
        
        # If a playing XI was selected, verify it's optimal
        if len(playing_xi) == 11:
            selected_score = sum(p.overall_score for p in playing_xi)
            
            # Find all valid combinations and their scores
            max_valid_score = -1
            for combo in combinations(players, 11):
                if is_valid_combination(combo):
                    combo_score = sum(p.overall_score for p in combo)
                    if combo_score > max_valid_score:
                        max_valid_score = combo_score
            
            # The selected XI should have the maximum score
            assert abs(selected_score - max_valid_score) < 0.01, \
                f"Selected XI score {selected_score} should equal max valid score {max_valid_score}"
        
        # Clean up - delete in correct order to avoid foreign key issues
        db_session.query(TeamPlayer).filter_by(team_id=team.id).delete()
        db_session.commit()
        for player in players:
            db_session.delete(player)
        db_session.delete(team)
        db_session.delete(room)
        db_session.commit()



# Feature: ipl-mock-auction-arena, Property 31: Bench player identification
# Validates: Requirements 12.1
@settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
@given(
    host_username=st.text(alphabet=string.ascii_letters + string.digits, min_size=1, max_size=50),
    team_name=st.text(alphabet=string.ascii_letters + string.digits + ' ', min_size=1, max_size=50),
    players=team_with_players_strategy(min_players=12, max_players=14)
)
def test_bench_player_identification(app, db_session, host_username, team_name, players):
    """
    Property 31: Bench player identification
    For any team with a finalized playing XI, the bench players should be 
    exactly those players in the squad who are not in the playing XI.
    """
    with app.app_context():
        import uuid
        
        # Create room with unique code
        room = Room(
            code=f"TEST{uuid.uuid4().hex[:8].upper()}",
            host_username=host_username
        )
        db_session.add(room)
        db_session.commit()
        
        # Create team
        team = Team(
            room_id=room.id,
            username=host_username,
            team_name=team_name,
            initial_purse=1000.0,
            purse_left=1000.0
        )
        db_session.add(team)
        db_session.commit()
        
        # Add players to database and team
        for player in players:
            db_session.add(player)
            db_session.commit()
            
            team_player = TeamPlayer(
                team_id=team.id,
                player_id=player.id,
                price=10.0
            )
            db_session.add(team_player)
        
        db_session.commit()
        
        # Select playing XI
        playing_xi = select_playing_xi(team.id)
        
        # If a playing XI was selected, verify bench identification
        if len(playing_xi) == 11:
            # Get bench players from database
            bench_tps = TeamPlayer.query.filter_by(
                team_id=team.id,
                in_playing_xi=False
            ).all()
            bench_player_ids = {tp.player_id for tp in bench_tps}
            
            # Get playing XI player IDs
            playing_xi_ids = {p.id for p in playing_xi}
            
            # Get all player IDs
            all_player_ids = {p.id for p in players}
            
            # Verify bench = all - playing XI
            expected_bench_ids = all_player_ids - playing_xi_ids
            assert bench_player_ids == expected_bench_ids, \
                f"Bench players should be exactly those not in playing XI"
            
            # Verify no overlap
            assert len(bench_player_ids & playing_xi_ids) == 0, \
                f"Bench and playing XI should not overlap"
        
        # Clean up
        db_session.query(TeamPlayer).filter_by(team_id=team.id).delete()
        db_session.commit()
        for player in players:
            db_session.delete(player)
        db_session.delete(team)
        db_session.delete(room)
        db_session.commit()



# Feature: ipl-mock-auction-arena, Property 32: Impact player selection
# Validates: Requirements 12.2
@settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
@given(
    host_username=st.text(alphabet=string.ascii_letters + string.digits, min_size=1, max_size=50),
    team_name=st.text(alphabet=string.ascii_letters + string.digits + ' ', min_size=1, max_size=50),
    players=team_with_players_strategy(min_players=12, max_players=14)
)
def test_impact_player_selection(app, db_session, host_username, team_name, players):
    """
    Property 32: Impact player selection
    For any team, the impact player should be the bench player with the 
    highest overall score.
    """
    with app.app_context():
        import uuid
        from app.services.ai_service import select_impact_player
        
        # Create room with unique code
        room = Room(
            code=f"TEST{uuid.uuid4().hex[:8].upper()}",
            host_username=host_username
        )
        db_session.add(room)
        db_session.commit()
        
        # Create team
        team = Team(
            room_id=room.id,
            username=host_username,
            team_name=team_name,
            initial_purse=1000.0,
            purse_left=1000.0
        )
        db_session.add(team)
        db_session.commit()
        
        # Add players to database and team
        for player in players:
            db_session.add(player)
            db_session.commit()
            
            team_player = TeamPlayer(
                team_id=team.id,
                player_id=player.id,
                price=10.0
            )
            db_session.add(team_player)
        
        db_session.commit()
        
        # Select playing XI
        playing_xi = select_playing_xi(team.id)
        
        # If a playing XI was selected and there are bench players
        if len(playing_xi) == 11 and len(players) > 11:
            # Select impact player
            impact_player = select_impact_player(team.id)
            
            if impact_player:
                # Get bench players
                bench_tps = TeamPlayer.query.filter_by(
                    team_id=team.id,
                    in_playing_xi=False
                ).all()
                bench_players = [Player.query.get(tp.player_id) for tp in bench_tps]
                
                # Find highest-rated bench player
                max_score = max(p.overall_score for p in bench_players)
                
                # Impact player should have the max score
                assert impact_player.overall_score == max_score, \
                    f"Impact player score {impact_player.overall_score} should equal max bench score {max_score}"
        
        # Clean up
        db_session.query(TeamPlayer).filter_by(team_id=team.id).delete()
        db_session.commit()
        for player in players:
            db_session.delete(player)
        db_session.delete(team)
        db_session.delete(room)
        db_session.commit()



# Feature: ipl-mock-auction-arena, Property 33: Impact player database marking
# Validates: Requirements 12.3
@settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
@given(
    host_username=st.text(alphabet=string.ascii_letters + string.digits, min_size=1, max_size=50),
    team_name=st.text(alphabet=string.ascii_letters + string.digits + ' ', min_size=1, max_size=50),
    players=team_with_players_strategy(min_players=12, max_players=14)
)
def test_impact_player_database_marking(app, db_session, host_username, team_name, players):
    """
    Property 33: Impact player database marking
    For any selected impact player, the team_players record should have 
    is_impact_player set to true.
    """
    with app.app_context():
        import uuid
        from app.services.ai_service import select_impact_player
        
        # Create room with unique code
        room = Room(
            code=f"TEST{uuid.uuid4().hex[:8].upper()}",
            host_username=host_username
        )
        db_session.add(room)
        db_session.commit()
        
        # Create team
        team = Team(
            room_id=room.id,
            username=host_username,
            team_name=team_name,
            initial_purse=1000.0,
            purse_left=1000.0
        )
        db_session.add(team)
        db_session.commit()
        
        # Add players to database and team
        for player in players:
            db_session.add(player)
            db_session.commit()
            
            team_player = TeamPlayer(
                team_id=team.id,
                player_id=player.id,
                price=10.0
            )
            db_session.add(team_player)
        
        db_session.commit()
        
        # Select playing XI
        playing_xi = select_playing_xi(team.id)
        
        # If a playing XI was selected and there are bench players
        if len(playing_xi) == 11 and len(players) > 11:
            # Select impact player
            impact_player = select_impact_player(team.id)
            
            if impact_player:
                # Get the team_player record for the impact player
                impact_tp = TeamPlayer.query.filter_by(
                    team_id=team.id,
                    player_id=impact_player.id
                ).first()
                
                # Verify is_impact_player is set to True
                assert impact_tp is not None, "Impact player should have a team_player record"
                assert impact_tp.is_impact_player is True, \
                    f"Impact player's is_impact_player flag should be True"
                
                # Verify only one player is marked as impact player
                impact_count = TeamPlayer.query.filter_by(
                    team_id=team.id,
                    is_impact_player=True
                ).count()
                assert impact_count == 1, \
                    f"Exactly one player should be marked as impact player, got {impact_count}"
        
        # Clean up
        db_session.query(TeamPlayer).filter_by(team_id=team.id).delete()
        db_session.commit()
        for player in players:
            db_session.delete(player)
        db_session.delete(team)
        db_session.delete(room)
        db_session.commit()



# Feature: ipl-mock-auction-arena, Property 34: Team rating components computation
# Validates: Requirements 13.1, 13.2, 13.3, 13.4, 13.5
@settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
@given(
    host_username=st.text(alphabet=string.ascii_letters + string.digits, min_size=1, max_size=50),
    team_name=st.text(alphabet=string.ascii_letters + string.digits + ' ', min_size=1, max_size=50),
    players=team_with_players_strategy(min_players=12, max_players=14)
)
def test_team_rating_components_computation(app, db_session, host_username, team_name, players):
    """
    Property 34: Team rating components computation
    For any team after auction completion, the system should compute batting rating, 
    bowling rating, balance score, bench depth, and role coverage score.
    """
    with app.app_context():
        import uuid
        from app.services.ai_service import calculate_team_rating
        from app.models.team_rating import TeamRating
        
        # Create room with unique code
        room = Room(
            code=f"TEST{uuid.uuid4().hex[:8].upper()}",
            host_username=host_username
        )
        db_session.add(room)
        db_session.commit()
        
        # Create team
        team = Team(
            room_id=room.id,
            username=host_username,
            team_name=team_name,
            initial_purse=1000.0,
            purse_left=1000.0
        )
        db_session.add(team)
        db_session.commit()
        
        # Add players to database and team
        for player in players:
            db_session.add(player)
            db_session.commit()
            
            team_player = TeamPlayer(
                team_id=team.id,
                player_id=player.id,
                price=10.0
            )
            db_session.add(team_player)
        
        db_session.commit()
        
        # Select playing XI
        playing_xi = select_playing_xi(team.id)
        
        # If a playing XI was selected
        if len(playing_xi) == 11:
            # Calculate team rating
            team_rating = calculate_team_rating(team.id)
            
            if team_rating:
                # Verify all components are computed
                assert team_rating.batting_rating is not None, \
                    "Batting rating should be computed"
                assert team_rating.bowling_rating is not None, \
                    "Bowling rating should be computed"
                assert team_rating.balance_score is not None, \
                    "Balance score should be computed"
                assert team_rating.bench_depth is not None, \
                    "Bench depth should be computed"
                assert team_rating.role_coverage is not None, \
                    "Role coverage should be computed"
                
                # Verify components are non-negative
                assert team_rating.batting_rating >= 0, \
                    "Batting rating should be non-negative"
                assert team_rating.bowling_rating >= 0, \
                    "Bowling rating should be non-negative"
                assert team_rating.balance_score >= 0, \
                    "Balance score should be non-negative"
                assert team_rating.bench_depth >= 0, \
                    "Bench depth should be non-negative"
                assert team_rating.role_coverage >= 0, \
                    "Role coverage should be non-negative"
        
        # Clean up
        TeamRating.query.filter_by(team_id=team.id).delete()
        db_session.query(TeamPlayer).filter_by(team_id=team.id).delete()
        db_session.commit()
        for player in players:
            db_session.delete(player)
        db_session.delete(team)
        db_session.delete(room)
        db_session.commit()



# Feature: ipl-mock-auction-arena, Property 35: Overall rating formula application
# Validates: Requirements 13.6
@settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
@given(
    host_username=st.text(alphabet=string.ascii_letters + string.digits, min_size=1, max_size=50),
    team_name=st.text(alphabet=string.ascii_letters + string.digits + ' ', min_size=1, max_size=50),
    players=team_with_players_strategy(min_players=12, max_players=14)
)
def test_overall_rating_formula(app, db_session, host_username, team_name, players):
    """
    Property 35: Overall rating formula application
    For any team with component ratings, the overall rating should equal 
    the weighted sum: 0.6 × avg_score_XI + 0.3 × balance_score + 0.1 × bench_depth.
    """
    with app.app_context():
        import uuid
        from app.services.ai_service import calculate_team_rating
        from app.models.team_rating import TeamRating
        
        # Create room with unique code
        room = Room(
            code=f"TEST{uuid.uuid4().hex[:8].upper()}",
            host_username=host_username
        )
        db_session.add(room)
        db_session.commit()
        
        # Create team
        team = Team(
            room_id=room.id,
            username=host_username,
            team_name=team_name,
            initial_purse=1000.0,
            purse_left=1000.0
        )
        db_session.add(team)
        db_session.commit()
        
        # Add players to database and team
        for player in players:
            db_session.add(player)
            db_session.commit()
            
            team_player = TeamPlayer(
                team_id=team.id,
                player_id=player.id,
                price=10.0
            )
            db_session.add(team_player)
        
        db_session.commit()
        
        # Select playing XI
        playing_xi = select_playing_xi(team.id)
        
        # If a playing XI was selected
        if len(playing_xi) == 11:
            # Calculate team rating
            team_rating = calculate_team_rating(team.id)
            
            if team_rating:
                # Calculate expected overall rating using the formula
                avg_score_xi = sum(p.overall_score for p in playing_xi) / len(playing_xi)
                expected_overall = (0.6 * avg_score_xi) + (0.3 * team_rating.balance_score) + (0.1 * team_rating.bench_depth)
                
                # Normalize to 0-100 scale
                expected_overall = min(100, max(0, expected_overall))
                
                # Verify the formula is applied correctly (with small tolerance for floating point)
                assert abs(team_rating.overall_rating - expected_overall) < 0.1, \
                    f"Overall rating {team_rating.overall_rating} should equal formula result {expected_overall}"
        
        # Clean up
        TeamRating.query.filter_by(team_id=team.id).delete()
        db_session.query(TeamPlayer).filter_by(team_id=team.id).delete()
        db_session.commit()
        for player in players:
            db_session.delete(player)
        db_session.delete(team)
        db_session.delete(room)
        db_session.commit()



# Feature: ipl-mock-auction-arena, Property 36: Rating normalization
# Validates: Requirements 13.7
@settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
@given(
    host_username=st.text(alphabet=string.ascii_letters + string.digits, min_size=1, max_size=50),
    team_name=st.text(alphabet=string.ascii_letters + string.digits + ' ', min_size=1, max_size=50),
    players=team_with_players_strategy(min_players=12, max_players=14)
)
def test_rating_normalization(app, db_session, host_username, team_name, players):
    """
    Property 36: Rating normalization
    For any computed team rating, the value should be in the range [0, 100].
    """
    with app.app_context():
        import uuid
        from app.services.ai_service import calculate_team_rating
        from app.models.team_rating import TeamRating
        
        # Create room with unique code
        room = Room(
            code=f"TEST{uuid.uuid4().hex[:8].upper()}",
            host_username=host_username
        )
        db_session.add(room)
        db_session.commit()
        
        # Create team
        team = Team(
            room_id=room.id,
            username=host_username,
            team_name=team_name,
            initial_purse=1000.0,
            purse_left=1000.0
        )
        db_session.add(team)
        db_session.commit()
        
        # Add players to database and team
        for player in players:
            db_session.add(player)
            db_session.commit()
            
            team_player = TeamPlayer(
                team_id=team.id,
                player_id=player.id,
                price=10.0
            )
            db_session.add(team_player)
        
        db_session.commit()
        
        # Select playing XI
        playing_xi = select_playing_xi(team.id)
        
        # If a playing XI was selected
        if len(playing_xi) == 11:
            # Calculate team rating
            team_rating = calculate_team_rating(team.id)
            
            if team_rating:
                # Verify overall rating is in [0, 100] range
                assert 0 <= team_rating.overall_rating <= 100, \
                    f"Overall rating {team_rating.overall_rating} should be in range [0, 100]"
        
        # Clean up
        TeamRating.query.filter_by(team_id=team.id).delete()
        db_session.query(TeamPlayer).filter_by(team_id=team.id).delete()
        db_session.commit()
        for player in players:
            db_session.delete(player)
        db_session.delete(team)
        db_session.delete(room)
        db_session.commit()



# Feature: ipl-mock-auction-arena, Property 37: Winner determination
# Validates: Requirements 14.1
@settings(max_examples=30, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
@given(
    room_code_suffix=st.text(alphabet=string.ascii_letters + string.digits, min_size=1, max_size=10),
    num_teams=st.integers(min_value=2, max_value=5)
)
def test_winner_determination(app, db_session, room_code_suffix, num_teams):
    """
    Property 37: Winner determination
    For any completed auction with multiple teams, the winning team should be 
    the one with the highest overall rating.
    """
    with app.app_context():
        import uuid
        from app.services.ai_service import determine_winner, calculate_team_rating
        from app.models.team_rating import TeamRating
        
        # Create room with unique code
        room_code = f"TEST{uuid.uuid4().hex[:8].upper()}"
        room = Room(
            code=room_code,
            host_username="host"
        )
        db_session.add(room)
        db_session.commit()
        
        teams = []
        team_ratings_dict = {}
        
        # Create multiple teams with players
        for i in range(num_teams):
            # Create team
            team = Team(
                room_id=room.id,
                username=f"user{i}",
                team_name=f"Team{i}",
                initial_purse=1000.0,
                purse_left=1000.0
            )
            db_session.add(team)
            db_session.commit()
            teams.append(team)
            
            # Generate players for this team
            players = []
            # 1 WK
            players.append(Player(
                name=f"WK{i}",
                role='WK',
                country='India',
                base_price=10.0,
                batting_score=50.0 + i * 5,
                bowling_score=30.0,
                overall_score=40.0 + i * 5,
                is_overseas=False
            ))
            # 3 BAT
            for j in range(3):
                players.append(Player(
                    name=f"BAT{i}_{j}",
                    role='BAT',
                    country='India',
                    base_price=10.0,
                    batting_score=50.0 + i * 5,
                    bowling_score=20.0,
                    overall_score=40.0 + i * 5,
                    is_overseas=False
                ))
            # 2 BOWL
            for j in range(2):
                players.append(Player(
                    name=f"BOWL{i}_{j}",
                    role='BOWL',
                    country='India',
                    base_price=10.0,
                    batting_score=20.0,
                    bowling_score=50.0 + i * 5,
                    overall_score=40.0 + i * 5,
                    is_overseas=False
                ))
            # 2 AR
            for j in range(2):
                players.append(Player(
                    name=f"AR{i}_{j}",
                    role='AR',
                    country='India',
                    base_price=10.0,
                    batting_score=40.0 + i * 5,
                    bowling_score=40.0 + i * 5,
                    overall_score=40.0 + i * 5,
                    is_overseas=False
                ))
            # 3 bench players
            for j in range(3):
                players.append(Player(
                    name=f"BENCH{i}_{j}",
                    role='BAT',
                    country='India',
                    base_price=10.0,
                    batting_score=30.0,
                    bowling_score=20.0,
                    overall_score=25.0,
                    is_overseas=False
                ))
            
            # Add players to database and team
            for player in players:
                db_session.add(player)
                db_session.commit()
                
                team_player = TeamPlayer(
                    team_id=team.id,
                    player_id=player.id,
                    price=10.0,
                    in_playing_xi=(players.index(player) < 11)  # First 11 are in playing XI
                )
                db_session.add(team_player)
            
            db_session.commit()
            
            # Calculate team rating
            team_rating = calculate_team_rating(team.id)
            if team_rating:
                team_ratings_dict[team.id] = team_rating.overall_rating
        
        # Determine winner
        winner = determine_winner(room_code)
        
        if winner and len(team_ratings_dict) > 0:
            # Find the team with highest rating
            max_rating = max(team_ratings_dict.values())
            expected_winner_ids = [tid for tid, rating in team_ratings_dict.items() if rating == max_rating]
            
            # Winner should be one of the teams with max rating
            assert winner.id in expected_winner_ids, \
                f"Winner team {winner.id} with rating {team_ratings_dict.get(winner.id)} should have the highest rating {max_rating}"
        
        # Clean up
        for team in teams:
            TeamRating.query.filter_by(team_id=team.id).delete()
            team_players = TeamPlayer.query.filter_by(team_id=team.id).all()
            for tp in team_players:
                player = Player.query.get(tp.player_id)
                db_session.delete(tp)
                if player:
                    db_session.delete(player)
            db_session.delete(team)
        db_session.delete(room)
        db_session.commit()
