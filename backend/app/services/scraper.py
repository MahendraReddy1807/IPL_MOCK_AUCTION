"""Web scraping module for player data."""
print("Starting scraper module import...")
import csv
import os
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
import pandas as pd
print("Imports successful...")


def calculate_batting_score(stats: Dict) -> float:
    """
    Calculate batting score from raw statistics.
    
    Args:
        stats: Dictionary containing batting statistics (runs, average, strike_rate, etc.)
    
    Returns:
        Batting score as a float
    """
    # Extract stats with defaults
    runs = stats.get('runs', 0)
    average = stats.get('average', 0)
    strike_rate = stats.get('strike_rate', 0)
    
    # Weighted formula for batting score
    # Normalize to 0-100 scale
    batting_score = (runs / 100) * 0.4 + average * 0.3 + (strike_rate / 2) * 0.3
    return min(batting_score, 100.0)


def calculate_bowling_score(stats: Dict) -> float:
    """
    Calculate bowling score from raw statistics.
    
    Args:
        stats: Dictionary containing bowling statistics (wickets, economy, average, etc.)
    
    Returns:
        Bowling score as a float
    """
    # Extract stats with defaults
    wickets = stats.get('wickets', 0)
    economy = stats.get('economy', 10)  # Lower is better
    bowling_avg = stats.get('bowling_average', 50)  # Lower is better
    
    # Weighted formula for bowling score
    # Normalize to 0-100 scale
    wickets_score = min(wickets * 2, 50)  # Cap at 50
    economy_score = max(0, (10 - economy) * 5)  # Lower economy = higher score
    avg_score = max(0, (50 - bowling_avg) / 2)  # Lower average = higher score
    
    bowling_score = wickets_score * 0.5 + economy_score * 0.3 + avg_score * 0.2
    return min(bowling_score, 100.0)


def calculate_overall_score(batting_score: float, bowling_score: float, role: str) -> float:
    """
    Compute overall player score based on role and statistics.
    
    Args:
        batting_score: Player's batting score
        bowling_score: Player's bowling score
        role: Player's role (BAT, BOWL, AR, WK)
    
    Returns:
        Overall score as a float
    """
    if role == 'BAT':
        # Batsmen: 80% batting, 20% bowling
        return batting_score * 0.8 + bowling_score * 0.2
    elif role == 'BOWL':
        # Bowlers: 20% batting, 80% bowling
        return batting_score * 0.2 + bowling_score * 0.8
    elif role == 'AR':
        # All-rounders: 50% batting, 50% bowling
        return batting_score * 0.5 + bowling_score * 0.5
    elif role == 'WK':
        # Wicket-keepers: 70% batting, 30% bowling (keeping not factored in this simple model)
        return batting_score * 0.7 + bowling_score * 0.3
    else:
        # Default: equal weight
        return batting_score * 0.5 + bowling_score * 0.5



def scrape_player_data(url: Optional[str] = None) -> pd.DataFrame:
    """
    Scrape player data from external source.
    
    Args:
        url: URL to scrape from (optional, uses default if not provided)
    
    Returns:
        DataFrame containing player data
    
    Raises:
        Exception: If scraping fails
    """
    # This is a placeholder implementation
    # In a real scenario, you would scrape from an actual IPL statistics website
    # For now, we'll create sample data
    
    if url:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Parse the HTML and extract player data
            # This would be specific to the website structure
            # Placeholder for actual scraping logic
            players_data = []
            
            # Example parsing (would need to be adapted to actual website)
            # player_rows = soup.find_all('tr', class_='player-row')
            # for row in player_rows:
            #     player_data = extract_player_from_row(row)
            #     players_data.append(player_data)
            
            return pd.DataFrame(players_data)
        except Exception as e:
            print(f"Scraping failed: {e}")
            raise
    
    # Generate sample data for development
    sample_data = generate_sample_player_data()
    return pd.DataFrame(sample_data)


def generate_sample_player_data() -> List[Dict]:
    """
    Generate sample player data for development and testing.
    
    Returns:
        List of dictionaries containing player data
    """
    players = [
        # Batsmen
        {'name': 'Virat Kohli', 'role': 'BAT', 'country': 'India', 'base_price': 2.0, 
         'runs': 7000, 'average': 50.0, 'strike_rate': 130.0, 'wickets': 5, 'economy': 9.0, 'bowling_average': 40.0},
        {'name': 'Rohit Sharma', 'role': 'BAT', 'country': 'India', 'base_price': 2.0,
         'runs': 6500, 'average': 48.0, 'strike_rate': 135.0, 'wickets': 3, 'economy': 10.0, 'bowling_average': 45.0},
        {'name': 'David Warner', 'role': 'BAT', 'country': 'Australia', 'base_price': 2.0,
         'runs': 6000, 'average': 45.0, 'strike_rate': 140.0, 'wickets': 0, 'economy': 12.0, 'bowling_average': 50.0},
        {'name': 'Jos Buttler', 'role': 'WK', 'country': 'England', 'base_price': 2.0,
         'runs': 5500, 'average': 42.0, 'strike_rate': 145.0, 'wickets': 0, 'economy': 11.0, 'bowling_average': 50.0},
        
        # All-rounders
        {'name': 'Hardik Pandya', 'role': 'AR', 'country': 'India', 'base_price': 2.0,
         'runs': 3000, 'average': 35.0, 'strike_rate': 150.0, 'wickets': 80, 'economy': 8.5, 'bowling_average': 28.0},
        {'name': 'Ravindra Jadeja', 'role': 'AR', 'country': 'India', 'base_price': 2.0,
         'runs': 2500, 'average': 30.0, 'strike_rate': 125.0, 'wickets': 130, 'economy': 7.5, 'bowling_average': 25.0},
        {'name': 'Glenn Maxwell', 'role': 'AR', 'country': 'Australia', 'base_price': 2.0,
         'runs': 3500, 'average': 32.0, 'strike_rate': 155.0, 'wickets': 60, 'economy': 8.0, 'bowling_average': 30.0},
        
        # Bowlers
        {'name': 'Jasprit Bumrah', 'role': 'BOWL', 'country': 'India', 'base_price': 2.0,
         'runs': 200, 'average': 10.0, 'strike_rate': 100.0, 'wickets': 150, 'economy': 7.0, 'bowling_average': 22.0},
        {'name': 'Rashid Khan', 'role': 'BOWL', 'country': 'Afghanistan', 'base_price': 2.0,
         'runs': 500, 'average': 15.0, 'strike_rate': 120.0, 'wickets': 140, 'economy': 6.5, 'bowling_average': 20.0},
        {'name': 'Kagiso Rabada', 'role': 'BOWL', 'country': 'South Africa', 'base_price': 2.0,
         'runs': 150, 'average': 8.0, 'strike_rate': 90.0, 'wickets': 130, 'economy': 8.0, 'bowling_average': 24.0},
        
        # More players for variety
        {'name': 'KL Rahul', 'role': 'WK', 'country': 'India', 'base_price': 1.5,
         'runs': 4500, 'average': 40.0, 'strike_rate': 135.0, 'wickets': 0, 'economy': 12.0, 'bowling_average': 50.0},
        {'name': 'Suryakumar Yadav', 'role': 'BAT', 'country': 'India', 'base_price': 1.5,
         'runs': 3000, 'average': 38.0, 'strike_rate': 145.0, 'wickets': 2, 'economy': 10.0, 'bowling_average': 45.0},
        {'name': 'Mohammed Shami', 'role': 'BOWL', 'country': 'India', 'base_price': 1.5,
         'runs': 100, 'average': 7.0, 'strike_rate': 80.0, 'wickets': 120, 'economy': 8.5, 'bowling_average': 26.0},
        {'name': 'Yuzvendra Chahal', 'role': 'BOWL', 'country': 'India', 'base_price': 1.5,
         'runs': 80, 'average': 6.0, 'strike_rate': 70.0, 'wickets': 125, 'economy': 7.8, 'bowling_average': 25.0},
        {'name': 'Andre Russell', 'role': 'AR', 'country': 'West Indies', 'base_price': 2.0,
         'runs': 2000, 'average': 28.0, 'strike_rate': 175.0, 'wickets': 70, 'economy': 9.0, 'bowling_average': 32.0},
    ]
    
    return players



def process_player_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process raw player data and calculate scores.
    
    Args:
        df: DataFrame with raw player data
    
    Returns:
        DataFrame with calculated batting, bowling, and overall scores
    """
    processed_data = []
    
    for _, row in df.iterrows():
        # Calculate batting score
        batting_stats = {
            'runs': row.get('runs', 0),
            'average': row.get('average', 0),
            'strike_rate': row.get('strike_rate', 0)
        }
        batting_score = calculate_batting_score(batting_stats)
        
        # Calculate bowling score
        bowling_stats = {
            'wickets': row.get('wickets', 0),
            'economy': row.get('economy', 10),
            'bowling_average': row.get('bowling_average', 50)
        }
        bowling_score = calculate_bowling_score(bowling_stats)
        
        # Calculate overall score
        overall_score = calculate_overall_score(batting_score, bowling_score, row['role'])
        
        # Determine if overseas
        is_overseas = row['country'] != 'India'
        
        processed_data.append({
            'name': row['name'],
            'role': row['role'],
            'country': row['country'],
            'base_price': row['base_price'],
            'batting_score': round(batting_score, 2),
            'bowling_score': round(bowling_score, 2),
            'overall_score': round(overall_score, 2),
            'is_overseas': is_overseas
        })
    
    return pd.DataFrame(processed_data)


def save_to_csv(df: pd.DataFrame, filepath: str = 'players_data.csv') -> None:
    """
    Save player data to CSV file.
    
    Args:
        df: DataFrame containing player data
        filepath: Path to save the CSV file
    """
    df.to_csv(filepath, index=False)
    print(f"Player data saved to {filepath}")


def import_players_from_csv(filepath: str = 'players_data.csv') -> int:
    """
    Import player data from CSV file to database.
    
    Args:
        filepath: Path to the CSV file
    
    Returns:
        Number of players imported
    """
    # Import here to avoid circular imports
    from app import db
    from app.models.player import Player
    
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"CSV file not found: {filepath}")
    
    df = pd.read_csv(filepath)
    count = 0
    
    for _, row in df.iterrows():
        # Check if player already exists
        existing_player = Player.query.filter_by(name=row['name']).first()
        if existing_player:
            print(f"Player {row['name']} already exists, skipping...")
            continue
        
        player = Player(
            name=row['name'],
            role=row['role'],
            country=row['country'],
            base_price=row['base_price'],
            batting_score=row['batting_score'],
            bowling_score=row['bowling_score'],
            overall_score=row['overall_score'],
            is_overseas=row['is_overseas']
        )
        db.session.add(player)
        count += 1
    
    db.session.commit()
    print(f"Imported {count} players to database")
    return count


def scrape_and_import_players(url: Optional[str] = None, csv_path: str = 'players_data.csv') -> int:
    """
    Complete workflow: scrape, process, save to CSV, and import to database.
    Falls back to existing CSV if scraping fails.
    
    Args:
        url: URL to scrape from (optional)
        csv_path: Path to save/load CSV file
    
    Returns:
        Number of players imported
    """
    try:
        # Try to scrape data
        print("Attempting to scrape player data...")
        raw_data = scrape_player_data(url)
        
        # Process the data
        print("Processing player data...")
        processed_data = process_player_data(raw_data)
        
        # Save to CSV
        print("Saving to CSV...")
        save_to_csv(processed_data, csv_path)
        
    except Exception as e:
        print(f"Scraping/processing failed: {e}")
        print(f"Attempting to use existing CSV file: {csv_path}")
        
        if not os.path.exists(csv_path):
            print("No existing CSV found. Generating sample data...")
            raw_data = scrape_player_data()
            processed_data = process_player_data(raw_data)
            save_to_csv(processed_data, csv_path)
    
    # Import to database
    print("Importing to database...")
    count = import_players_from_csv(csv_path)
    return count
