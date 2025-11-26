"""Database initialization script."""
from app import create_app, db
from app.models import User, Room, Team, Player, AuctionPlayer, TeamPlayer, TeamRating
from app.services.scraper import scrape_and_import_players


def init_database(import_players: bool = True):
    """Initialize the database with tables."""
    app = create_app()
    
    with app.app_context():
        # Drop all tables (use with caution in production)
        db.drop_all()
        
        # Create all tables
        db.create_all()
        
        print("Database initialized successfully!")
        print("Tables created:")
        print("  - users")
        print("  - rooms")
        print("  - teams")
        print("  - players")
        print("  - auction_players")
        print("  - team_players")
        print("  - team_ratings")
        
        # Import player data
        if import_players:
            print("\nImporting player data...")
            try:
                count = scrape_and_import_players()
                print(f"Successfully imported {count} players!")
            except Exception as e:
                print(f"Failed to import players: {e}")


if __name__ == '__main__':
    init_database()
