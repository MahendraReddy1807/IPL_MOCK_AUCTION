"""Property-based tests for scraper module."""
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck, assume
from app.services.scraper import (
    calculate_batting_score,
    calculate_bowling_score,
    calculate_overall_score,
    process_player_data,
    scrape_player_data
)
import pandas as pd


# Feature: ipl-mock-auction-arena, Property 14: Scraped player data completeness
# Validates: Requirements 6.2
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    use_url=st.booleans()
)
def test_scraped_player_data_completeness(app, use_url):
    """
    Property 14: Scraped player data completeness
    For any player scraped from external sources (or generated), 
    the data should include name, role, country, base price, 
    batting statistics, and bowling statistics.
    """
    with app.app_context():
        # Scrape player data (will use sample data since no URL provided)
        df = scrape_player_data(url=None)
        
        # Verify DataFrame is not empty
        assert len(df) > 0, "Scraped data should not be empty"
        
        # Required fields for raw data
        required_fields = ['name', 'role', 'country', 'base_price', 
                          'runs', 'average', 'strike_rate',  # batting stats
                          'wickets', 'economy', 'bowling_average']  # bowling stats
        
        # Check that all required fields are present
        for field in required_fields:
            assert field in df.columns, f"Missing required field: {field}"
        
        # Check that each player has all required fields with non-null values
        for idx, row in df.iterrows():
            for field in required_fields:
                assert pd.notna(row[field]), f"Player at index {idx} has null value for {field}"
                
                # Additional validation
                if field == 'name':
                    assert isinstance(row[field], str) and len(row[field]) > 0, \
                        f"Player name must be non-empty string"
                elif field == 'role':
                    assert row[field] in ['BAT', 'BOWL', 'AR', 'WK'], \
                        f"Invalid role: {row[field]}"
                elif field == 'country':
                    assert isinstance(row[field], str) and len(row[field]) > 0, \
                        f"Country must be non-empty string"
                elif field in ['base_price', 'runs', 'average', 'strike_rate', 
                              'wickets', 'economy', 'bowling_average']:
                    assert isinstance(row[field], (int, float)), \
                        f"{field} must be numeric"


# Feature: ipl-mock-auction-arena, Property 15: Overall score computation
# Validates: Requirements 6.5
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    batting_score=st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
    bowling_score=st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
    role=st.sampled_from(['BAT', 'BOWL', 'AR', 'WK'])
)
def test_overall_score_computation(app, batting_score, bowling_score, role):
    """
    Property 15: Overall score computation
    For any player with batting and bowling scores, an overall score 
    should be computed and stored.
    """
    with app.app_context():
        # Calculate overall score
        overall_score = calculate_overall_score(batting_score, bowling_score, role)
        
        # Verify overall score is computed (not None)
        assert overall_score is not None, "Overall score should be computed"
        
        # Verify overall score is a number
        assert isinstance(overall_score, (int, float)), \
            "Overall score should be numeric"
        
        # Verify overall score is within valid range [0, 100]
        assert 0.0 <= overall_score <= 100.0, \
            f"Overall score {overall_score} should be between 0 and 100"
        
        # Verify role-specific weighting
        if role == 'BAT':
            # Batsmen should weight batting more heavily
            expected = batting_score * 0.8 + bowling_score * 0.2
            assert abs(overall_score - expected) < 0.01, \
                f"BAT overall score should be 80% batting + 20% bowling"
        elif role == 'BOWL':
            # Bowlers should weight bowling more heavily
            expected = batting_score * 0.2 + bowling_score * 0.8
            assert abs(overall_score - expected) < 0.01, \
                f"BOWL overall score should be 20% batting + 80% bowling"
        elif role == 'AR':
            # All-rounders should weight equally
            expected = batting_score * 0.5 + bowling_score * 0.5
            assert abs(overall_score - expected) < 0.01, \
                f"AR overall score should be 50% batting + 50% bowling"
        elif role == 'WK':
            # Wicket-keepers should weight batting more
            expected = batting_score * 0.7 + bowling_score * 0.3
            assert abs(overall_score - expected) < 0.01, \
                f"WK overall score should be 70% batting + 30% bowling"


@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    runs=st.floats(min_value=0.0, max_value=10000.0, allow_nan=False, allow_infinity=False),
    average=st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
    strike_rate=st.floats(min_value=0.0, max_value=300.0, allow_nan=False, allow_infinity=False)
)
def test_batting_score_computation(app, runs, average, strike_rate):
    """
    Test that batting score is computed correctly from statistics.
    """
    with app.app_context():
        stats = {
            'runs': runs,
            'average': average,
            'strike_rate': strike_rate
        }
        
        batting_score = calculate_batting_score(stats)
        
        # Verify score is computed
        assert batting_score is not None
        assert isinstance(batting_score, (int, float))
        
        # Verify score is in valid range
        assert 0.0 <= batting_score <= 100.0, \
            f"Batting score {batting_score} should be between 0 and 100"


@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    wickets=st.floats(min_value=0.0, max_value=500.0, allow_nan=False, allow_infinity=False),
    economy=st.floats(min_value=3.0, max_value=15.0, allow_nan=False, allow_infinity=False),
    bowling_avg=st.floats(min_value=10.0, max_value=60.0, allow_nan=False, allow_infinity=False)
)
def test_bowling_score_computation(app, wickets, economy, bowling_avg):
    """
    Test that bowling score is computed correctly from statistics.
    """
    with app.app_context():
        stats = {
            'wickets': wickets,
            'economy': economy,
            'bowling_average': bowling_avg
        }
        
        bowling_score = calculate_bowling_score(stats)
        
        # Verify score is computed
        assert bowling_score is not None
        assert isinstance(bowling_score, (int, float))
        
        # Verify score is in valid range
        assert 0.0 <= bowling_score <= 100.0, \
            f"Bowling score {bowling_score} should be between 0 and 100"


def test_process_player_data_completeness(app):
    """
    Test that process_player_data adds all required computed fields.
    """
    with app.app_context():
        # Get raw data
        raw_df = scrape_player_data()
        
        # Process the data
        processed_df = process_player_data(raw_df)
        
        # Verify processed data has required fields
        required_fields = ['name', 'role', 'country', 'base_price',
                          'batting_score', 'bowling_score', 'overall_score', 'is_overseas']
        
        for field in required_fields:
            assert field in processed_df.columns, f"Missing field in processed data: {field}"
        
        # Verify all scores are computed for each player
        for idx, row in processed_df.iterrows():
            assert pd.notna(row['batting_score']), f"Player {row['name']} missing batting_score"
            assert pd.notna(row['bowling_score']), f"Player {row['name']} missing bowling_score"
            assert pd.notna(row['overall_score']), f"Player {row['name']} missing overall_score"
            assert pd.notna(row['is_overseas']), f"Player {row['name']} missing is_overseas"
            
            # Verify scores are in valid range
            assert 0.0 <= row['batting_score'] <= 100.0
            assert 0.0 <= row['bowling_score'] <= 100.0
            assert 0.0 <= row['overall_score'] <= 100.0
            
            # Verify is_overseas is boolean
            assert isinstance(row['is_overseas'], (bool, int))
