"""Team management service."""
import os
import uuid
from pathlib import Path
from models import get_session, Team, TeamPlayer, Player


def configure_team(room_id, username, team_name, purse, logo_url=None):
    """
    Configure team details for a user in a room.
    
    Args:
        room_id: ID of the room
        username: Username of the team owner
        team_name: Name of the team
        purse: Starting purse amount
        logo_url: Optional URL/path to team logo
        
    Returns:
        tuple: (success: bool, message: str, team: Team or None)
    """
    session = get_session()
    try:
        # Validate team name
        if not team_name or not team_name.strip():
            return False, "Team name cannot be empty", None
        
        # Validate purse amount
        if not isinstance(purse, (int, float)) or purse <= 0:
            return False, "Purse must be a positive number", None
        
        # Check if team already exists for this user in this room
        existing_team = session.query(Team).filter_by(room_id=room_id, username=username).first()
        if existing_team:
            # Update existing team
            existing_team.team_name = team_name.strip()
            existing_team.logo_url = logo_url
            existing_team.initial_purse = purse
            existing_team.purse_left = purse
            session.commit()
            return True, "Team updated successfully", existing_team
        
        # Create new team
        team = Team(
            room_id=room_id,
            username=username,
            team_name=team_name.strip(),
            logo_url=logo_url,
            initial_purse=purse,
            purse_left=purse
        )
        
        session.add(team)
        session.commit()
        
        return True, "Team configured successfully", team
    except Exception as e:
        session.rollback()
        return False, f"Error configuring team: {str(e)}", None
    finally:
        session.close()


def save_logo(uploaded_file, upload_folder='uploads/logos'):
    """
    Save uploaded team logo file.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        upload_folder: Directory to store uploaded files
        
    Returns:
        tuple: (success: bool, message: str, file_path: str or None)
    """
    if not uploaded_file:
        return False, "No file provided", None
    
    try:
        # Create upload directory if it doesn't exist
        upload_path = Path(upload_folder)
        upload_path.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        file_extension = Path(uploaded_file.name).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = upload_path / unique_filename
        
        # Save file
        with open(file_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        
        return True, "Logo uploaded successfully", str(file_path)
    except Exception as e:
        return False, f"Failed to upload logo: {str(e)}", None


def update_purse(team_id, amount):
    """
    Update team's remaining purse.
    
    Args:
        team_id: ID of the team
        amount: New purse amount
        
    Returns:
        tuple: (success: bool, message: str, team: Team or None)
    """
    session = get_session()
    try:
        team = session.query(Team).get(team_id)
        if not team:
            return False, "Team not found", None
        
        # Validate amount
        if not isinstance(amount, (int, float)) or amount < 0:
            return False, "Purse amount must be non-negative", None
        
        team.purse_left = amount
        session.commit()
        
        return True, "Purse updated successfully", team
    except Exception as e:
        session.rollback()
        return False, f"Error updating purse: {str(e)}", None
    finally:
        session.close()


def add_player_to_team(team_id, player_id, price):
    """
    Add a player to a team's squad.
    
    Args:
        team_id: ID of the team
        player_id: ID of the player
        price: Purchase price of the player
        
    Returns:
        tuple: (success: bool, message: str, team_player: TeamPlayer or None)
    """
    session = get_session()
    try:
        # Verify team exists
        team = session.query(Team).get(team_id)
        if not team:
            return False, "Team not found", None
        
        # Verify player exists
        player = session.query(Player).get(player_id)
        if not player:
            return False, "Player not found", None
        
        # Check if player already in team
        existing = session.query(TeamPlayer).filter_by(team_id=team_id, player_id=player_id).first()
        if existing:
            return False, "Player already in team", None
        
        # Create team player record
        team_player = TeamPlayer(
            team_id=team_id,
            player_id=player_id,
            price=price
        )
        
        session.add(team_player)
        
        # Deduct from purse
        team.purse_left -= price
        
        session.commit()
        
        return True, "Player added to team successfully", team_player
    except Exception as e:
        session.rollback()
        return False, f"Error adding player to team: {str(e)}", None
    finally:
        session.close()


def get_team_squad(team_id):
    """
    Get all players in a team's squad.
    
    Args:
        team_id: ID of the team
        
    Returns:
        list: List of Player objects
    """
    session = get_session()
    try:
        team = session.query(Team).get(team_id)
        if not team:
            return []
        
        # Get all team players
        team_players = session.query(TeamPlayer).filter_by(team_id=team_id).all()
        
        # Extract player objects
        players = [tp.player for tp in team_players]
        
        return players
    finally:
        session.close()


def get_team(room_code, username):
    """
    Get team for a user in a room.
    
    Args:
        room_code: Code of the room
        username: Username of the team owner
        
    Returns:
        Team or None: Team object if found
    """
    from models import Room
    session = get_session()
    try:
        room = session.query(Room).filter_by(code=room_code).first()
        if not room:
            return None
        
        return session.query(Team).filter_by(room_id=room.id, username=username).first()
    finally:
        session.close()


def get_all_teams(room_code):
    """
    Get all teams in a room.
    
    Args:
        room_code: Code of the room
        
    Returns:
        list: List of Team objects
    """
    from models import Room
    session = get_session()
    try:
        room = session.query(Room).filter_by(code=room_code).first()
        if not room:
            return []
        
        return session.query(Team).filter_by(room_id=room.id).all()
    finally:
        session.close()
