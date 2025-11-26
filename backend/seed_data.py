"""Seed script for development data."""
import csv
import random
from app import create_app, db
from app.models.player import Player
from app.models.room import Room
from app.models.user import User
from app.models.team import Team


def seed_players():
    """Seed players from real IPL data - 500+ real players with authentic base prices."""
    print("Seeding players...")
    
    # Check if players already exist
    existing_count = Player.query.count()
    if existing_count > 0:
        print(f"Players already seeded ({existing_count} players found). Skipping...")
        return
    
    # Import real player data
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    from data.real_players import REAL_IPL_PLAYERS, calculate_overall_score
    
    # Add all real IPL players
    print(f"Adding {len(REAL_IPL_PLAYERS)} real IPL players with authentic base prices...")
    for player_data in REAL_IPL_PLAYERS:
        overall_score = calculate_overall_score(
            player_data['batting_score'],
            player_data['bowling_score'],
            player_data['role']
        )
        
        player = Player(
            name=player_data['name'],
            role=player_data['role'],
            country=player_data['country'],
            base_price=player_data['base_price'],
            batting_score=player_data['batting_score'],
            bowling_score=player_data['bowling_score'],
            overall_score=round(overall_score, 2),
            is_overseas=player_data['is_overseas']
        )
        db.session.add(player)
    
    db.session.commit()
    final_count = Player.query.count()
    print(f"Successfully added all {final_count} real IPL players!")
    print(f"All players have authentic IPL auction base prices (0.3 Cr - 2.0 Cr)")


def seed_sample_room():
    """Create a sample room for testing."""
    print("Creating sample room...")
    
    # Check if sample room already exists
    existing_room = Room.query.filter_by(code='DEMO1234').first()
    if existing_room:
        print("Sample room already exists. Skipping...")
        return
    
    try:
        # Create sample room
        room = Room(
            code='DEMO1234',
            host_username='demo_host',
            status='lobby'
        )
        db.session.add(room)
        db.session.commit()
        
        # Create sample users (minimum 2 required)
        users = [
            User(username='demo_host', room_id=room.id),
            User(username='player1', room_id=room.id),
        ]
        
        for user in users:
            db.session.add(user)
        
        db.session.commit()
        
        # Create sample teams
        teams = [
            Team(
                room_id=room.id,
                username='demo_host',
                team_name='Mumbai Indians',
                logo_url='/logos/mi.png',
                initial_purse=100.0,
                purse_left=100.0
            ),
            Team(
                room_id=room.id,
                username='player1',
                team_name='Chennai Super Kings',
                logo_url='/logos/csk.png',
                initial_purse=100.0,
                purse_left=100.0
            ),
        ]
        
        for team in teams:
            db.session.add(team)
        
        db.session.commit()
        
        print(f"Successfully created sample room: DEMO1234")
        print(f"  - Host: demo_host")
        print(f"  - Participants: 2")
        print(f"  - Teams: 2")
        
    except Exception as e:
        print(f"Error creating sample room: {str(e)}")
        db.session.rollback()


def clear_all_data():
    """Clear all data from database (use with caution!)."""
    print("WARNING: This will delete all data from the database!")
    confirm = input("Type 'yes' to confirm: ")
    
    if confirm.lower() == 'yes':
        try:
            # Delete in correct order to avoid foreign key issues
            from app.models.team_rating import TeamRating
            from app.models.team_player import TeamPlayer
            from app.models.auction_player import AuctionPlayer
            
            TeamRating.query.delete()
            TeamPlayer.query.delete()
            AuctionPlayer.query.delete()
            Team.query.delete()
            User.query.delete()
            Room.query.delete()
            Player.query.delete()
            
            db.session.commit()
            print("All data cleared successfully!")
        except Exception as e:
            print(f"Error clearing data: {str(e)}")
            db.session.rollback()
    else:
        print("Operation cancelled.")


def main():
    """Main seed function."""
    app = create_app()
    
    with app.app_context():
        print("=" * 50)
        print("IPL Mock Auction Arena - Database Seeding")
        print("=" * 50)
        print()
        
        # Seed players
        seed_players()
        print()
        
        # Seed sample room
        seed_sample_room()
        print()
        
        print("=" * 50)
        print("Seeding complete!")
        print("=" * 50)
        print()
        print("Sample room details:")
        print("  Room Code: DEMO1234")
        print("  Host: demo_host")
        print("  Players: player1")
        print()
        print("You can now start the application and join this room for testing.")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--clear':
        app = create_app()
        with app.app_context():
            clear_all_data()
    else:
        main()
