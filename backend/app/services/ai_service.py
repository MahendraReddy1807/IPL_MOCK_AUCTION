"""AI analysis service for team selection and rating."""
from itertools import combinations
from app import db
from app.models.team import Team
from app.models.team_player import TeamPlayer
from app.models.player import Player
from app.models.team_rating import TeamRating


def select_playing_xi(team_id):
    """
    Select optimal playing XI for a team based on constraints.
    
    Constraints:
    - Exactly 11 players
    - Exactly 1 wicket-keeper (WK)
    - At least 3 batsmen (BAT)
    - At least 2 bowlers (BOWL)
    - Between 1 and 3 all-rounders (AR)
    - At most 4 overseas players
    
    Args:
        team_id: ID of the team
        
    Returns:
        list: List of Player objects in the playing XI
    """
    # Get all players for the team
    team_players = TeamPlayer.query.filter_by(team_id=team_id).all()
    
    if len(team_players) < 11:
        return []
    
    # Get player objects
    players = [Player.query.get(tp.player_id) for tp in team_players]
    
    # Generate all possible 11-player combinations
    best_combination = None
    best_score = -1
    
    for combo in combinations(players, 11):
        if is_valid_combination(combo):
            score = sum(p.overall_score for p in combo)
            if score > best_score:
                best_score = score
                best_combination = combo
    
    if best_combination:
        # Mark players as in playing XI
        for tp in team_players:
            tp.in_playing_xi = False
        
        for player in best_combination:
            tp = TeamPlayer.query.filter_by(team_id=team_id, player_id=player.id).first()
            if tp:
                tp.in_playing_xi = True
        
        db.session.commit()
        
        return list(best_combination)
    
    return []


def is_valid_combination(players):
    """
    Check if a combination of players meets all constraints.
    
    Args:
        players: Tuple or list of Player objects
        
    Returns:
        bool: True if valid, False otherwise
    """
    if len(players) != 11:
        return False
    
    # Count by role
    wk_count = sum(1 for p in players if p.role == 'WK')
    bat_count = sum(1 for p in players if p.role == 'BAT')
    bowl_count = sum(1 for p in players if p.role == 'BOWL')
    ar_count = sum(1 for p in players if p.role == 'AR')
    overseas_count = sum(1 for p in players if p.is_overseas)
    
    # Check constraints
    if wk_count != 1:
        return False
    if bat_count < 3:
        return False
    if bowl_count < 2:
        return False
    if ar_count < 1 or ar_count > 3:
        return False
    if overseas_count > 4:
        return False
    
    return True


def select_impact_player(team_id):
    """
    Select the impact player from bench (highest-rated player not in playing XI).
    
    Args:
        team_id: ID of the team
        
    Returns:
        Player or None: The selected impact player
    """
    # Get bench players (not in playing XI)
    team_players = TeamPlayer.query.filter_by(
        team_id=team_id,
        in_playing_xi=False
    ).all()
    
    if not team_players:
        return None
    
    # Find highest-rated bench player
    best_player = None
    best_score = -1
    
    for tp in team_players:
        player = Player.query.get(tp.player_id)
        if player and player.overall_score > best_score:
            best_score = player.overall_score
            best_player = player
            best_tp = tp
    
    if best_player:
        # Mark as impact player
        # First, clear any existing impact player
        for tp in TeamPlayer.query.filter_by(team_id=team_id).all():
            tp.is_impact_player = False
        
        best_tp.is_impact_player = True
        db.session.commit()
        
        return best_player
    
    return None


def calculate_team_rating(team_id):
    """
    Calculate comprehensive team rating.
    
    Args:
        team_id: ID of the team
        
    Returns:
        TeamRating: The calculated team rating object
    """
    # Get playing XI players
    playing_xi_tps = TeamPlayer.query.filter_by(
        team_id=team_id,
        in_playing_xi=True
    ).all()
    
    if not playing_xi_tps:
        return None
    
    playing_xi = [Player.query.get(tp.player_id) for tp in playing_xi_tps]
    
    # Get bench players
    bench_tps = TeamPlayer.query.filter_by(
        team_id=team_id,
        in_playing_xi=False
    ).all()
    bench = [Player.query.get(tp.player_id) for tp in bench_tps]
    
    # Calculate batting rating
    batting_players = [p for p in playing_xi if p.role in ['BAT', 'AR', 'WK']]
    batting_rating = sum(p.batting_score for p in batting_players) / len(batting_players) if batting_players else 0
    
    # Calculate bowling rating
    bowling_players = [p for p in playing_xi if p.role in ['BOWL', 'AR']]
    bowling_rating = sum(p.bowling_score for p in bowling_players) / len(bowling_players) if bowling_players else 0
    
    # Calculate balance score
    if batting_rating > 0 and bowling_rating > 0:
        balance_score = (min(batting_rating, bowling_rating) / max(batting_rating, bowling_rating)) * 100
    else:
        balance_score = 0
    
    # Calculate bench depth
    bench_depth = sum(p.overall_score for p in bench) / len(bench) if bench else 0
    
    # Calculate role coverage
    roles_covered = len(set(p.role for p in playing_xi))
    role_coverage = (roles_covered / 4) * 100  # 4 roles: BAT, BOWL, AR, WK
    
    # Calculate average score of playing XI
    avg_score_xi = sum(p.overall_score for p in playing_xi) / len(playing_xi)
    
    # Calculate overall rating using weighted formula
    overall_rating = (0.6 * avg_score_xi) + (0.3 * balance_score) + (0.1 * bench_depth)
    
    # Normalize to 0-100 scale
    # Assuming max possible overall_score is 100
    normalized_rating = min(100, max(0, overall_rating))
    
    # Store in database
    team_rating = TeamRating.query.filter_by(team_id=team_id).first()
    if not team_rating:
        team_rating = TeamRating(team_id=team_id)
        db.session.add(team_rating)
    
    team_rating.overall_rating = normalized_rating
    team_rating.batting_rating = batting_rating
    team_rating.bowling_rating = bowling_rating
    team_rating.balance_score = balance_score
    team_rating.bench_depth = bench_depth
    team_rating.role_coverage = role_coverage
    
    db.session.commit()
    
    return team_rating


def determine_winner(room_code):
    """
    Determine the winning team based on highest rating.
    
    Args:
        room_code: Code of the room
        
    Returns:
        Team or None: The winning team
    """
    from app.models.room import Room
    
    room = Room.query.filter_by(code=room_code).first()
    if not room:
        return None
    
    # Get all teams in the room
    teams = Team.query.filter_by(room_id=room.id).all()
    
    if not teams:
        return None
    
    # Find team with highest rating
    best_team = None
    best_rating = -1
    
    for team in teams:
        team_rating = TeamRating.query.filter_by(team_id=team.id).first()
        if team_rating and team_rating.overall_rating > best_rating:
            best_rating = team_rating.overall_rating
            best_team = team
    
    return best_team
