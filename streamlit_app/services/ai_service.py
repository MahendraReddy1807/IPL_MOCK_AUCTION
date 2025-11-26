"""AI analysis service for team selection and rating."""
from itertools import combinations
from models import get_session, Team, TeamPlayer, Player, TeamRating, Room


def select_playing_xi(team_id):
    """Select optimal playing XI for a team based on constraints."""
    session = get_session()
    try:
        team_players = session.query(TeamPlayer).filter_by(team_id=team_id).all()
        
        if len(team_players) < 11:
            return []
        
        players = [session.query(Player).get(tp.player_id) for tp in team_players]
        
        best_combination = None
        best_score = -1
        
        for combo in combinations(players, 11):
            if is_valid_combination(combo):
                score = sum(p.overall_score for p in combo)
                if score > best_score:
                    best_score = score
                    best_combination = combo
        
        if best_combination:
            for tp in team_players:
                tp.in_playing_xi = False
            
            for player in best_combination:
                tp = session.query(TeamPlayer).filter_by(team_id=team_id, player_id=player.id).first()
                if tp:
                    tp.in_playing_xi = True
            
            session.commit()
            
            return list(best_combination)
        
        return []
    except Exception as e:
        session.rollback()
        return []
    finally:
        session.close()


def is_valid_combination(players):
    """Check if a combination of players meets all constraints."""
    if len(players) != 11:
        return False
    
    wk_count = sum(1 for p in players if p.role == 'WK')
    bat_count = sum(1 for p in players if p.role == 'BAT')
    bowl_count = sum(1 for p in players if p.role == 'BOWL')
    ar_count = sum(1 for p in players if p.role == 'AR')
    overseas_count = sum(1 for p in players if p.is_overseas)
    
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
    """Select the impact player from bench."""
    session = get_session()
    try:
        team_players = session.query(TeamPlayer).filter_by(
            team_id=team_id,
            in_playing_xi=False
        ).all()
        
        if not team_players:
            return None
        
        best_player = None
        best_score = -1
        best_tp = None
        
        for tp in team_players:
            player = session.query(Player).get(tp.player_id)
            if player and player.overall_score > best_score:
                best_score = player.overall_score
                best_player = player
                best_tp = tp
        
        if best_player:
            for tp in session.query(TeamPlayer).filter_by(team_id=team_id).all():
                tp.is_impact_player = False
            
            best_tp.is_impact_player = True
            session.commit()
            
            return best_player
        
        return None
    except Exception as e:
        session.rollback()
        return None
    finally:
        session.close()


def calculate_team_rating(team_id):
    """Calculate comprehensive team rating."""
    session = get_session()
    try:
        playing_xi_tps = session.query(TeamPlayer).filter_by(
            team_id=team_id,
            in_playing_xi=True
        ).all()
        
        if not playing_xi_tps:
            return None
        
        playing_xi = [session.query(Player).get(tp.player_id) for tp in playing_xi_tps]
        
        bench_tps = session.query(TeamPlayer).filter_by(
            team_id=team_id,
            in_playing_xi=False
        ).all()
        bench = [session.query(Player).get(tp.player_id) for tp in bench_tps]
        
        batting_players = [p for p in playing_xi if p.role in ['BAT', 'AR', 'WK']]
        batting_rating = sum(p.batting_score for p in batting_players) / len(batting_players) if batting_players else 0
        
        bowling_players = [p for p in playing_xi if p.role in ['BOWL', 'AR']]
        bowling_rating = sum(p.bowling_score for p in bowling_players) / len(bowling_players) if bowling_players else 0
        
        if batting_rating > 0 and bowling_rating > 0:
            balance_score = (min(batting_rating, bowling_rating) / max(batting_rating, bowling_rating)) * 100
        else:
            balance_score = 0
        
        bench_depth = sum(p.overall_score for p in bench) / len(bench) if bench else 0
        
        roles_covered = len(set(p.role for p in playing_xi))
        role_coverage = (roles_covered / 4) * 100
        
        avg_score_xi = sum(p.overall_score for p in playing_xi) / len(playing_xi)
        
        overall_rating = (0.6 * avg_score_xi) + (0.3 * balance_score) + (0.1 * bench_depth)
        normalized_rating = min(100, max(0, overall_rating))
        
        team_rating = session.query(TeamRating).filter_by(team_id=team_id).first()
        if not team_rating:
            team_rating = TeamRating(team_id=team_id)
            session.add(team_rating)
        
        team_rating.overall_rating = normalized_rating
        team_rating.batting_rating = batting_rating
        team_rating.bowling_rating = bowling_rating
        team_rating.balance_score = balance_score
        team_rating.bench_depth = bench_depth
        team_rating.role_coverage = role_coverage
        
        session.commit()
        
        return team_rating
    except Exception as e:
        session.rollback()
        return None
    finally:
        session.close()


def determine_winner(room_code):
    """Determine the winning team based on highest rating."""
    session = get_session()
    try:
        room = session.query(Room).filter_by(code=room_code).first()
        if not room:
            return None
        
        teams = session.query(Team).filter_by(room_id=room.id).all()
        
        if not teams:
            return None
        
        best_team = None
        best_rating = -1
        
        for team in teams:
            team_rating = session.query(TeamRating).filter_by(team_id=team.id).first()
            if team_rating and team_rating.overall_rating > best_rating:
                best_rating = team_rating.overall_rating
                best_team = team
        
        return best_team
    finally:
        session.close()
