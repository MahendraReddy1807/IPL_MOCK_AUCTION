"""Data service for loading and seeding database."""
import pandas as pd
from pathlib import Path
from models import get_session, Player
from config import Config


def load_players_from_csv():
    """
    Load players from CSV file.
    
    Returns:
        list: List of player dictionaries
    """
    csv_path = Config.PLAYERS_CSV
    
    if not Path(csv_path).exists():
        return []
    
    try:
        df = pd.read_csv(csv_path)
        players = df.to_dict('records')
        return players
    except Exception as e:
        print(f"Error loading players from CSV: {e}")
        return []


def seed_database():
    """Seed database with players from CSV."""
    session = get_session()
    try:
        players_data = load_players_from_csv()
        
        for player_data in players_data:
            # Check if player already exists
            existing = session.query(Player).filter_by(name=player_data['name']).first()
            if existing:
                continue
            
            player = Player(
                name=player_data['name'],
                role=player_data['role'],
                country=player_data['country'],
                base_price=float(player_data['base_price']),
                batting_score=float(player_data['batting_score']),
                bowling_score=float(player_data['bowling_score']),
                overall_score=float(player_data['overall_score']),
                is_overseas=bool(player_data['is_overseas'])
            )
            session.add(player)
        
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print(f"Error seeding database: {e}")
        return False
    finally:
        session.close()


def seed_database_if_empty():
    """Seed database only if it's empty."""
    session = get_session()
    try:
        player_count = session.query(Player).count()
        if player_count == 0:
            return seed_database()
        return True
    finally:
        session.close()


def get_all_players():
    """Get all players from database."""
    session = get_session()
    try:
        return session.query(Player).all()
    finally:
        session.close()
