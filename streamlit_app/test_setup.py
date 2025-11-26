"""Test script to verify setup."""
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    
    try:
        import streamlit
        print("✓ Streamlit imported")
    except ImportError as e:
        print(f"✗ Streamlit import failed: {e}")
        return False
    
    try:
        import sqlalchemy
        print("✓ SQLAlchemy imported")
    except ImportError as e:
        print(f"✗ SQLAlchemy import failed: {e}")
        return False
    
    try:
        import pandas
        print("✓ Pandas imported")
    except ImportError as e:
        print(f"✗ Pandas import failed: {e}")
        return False
    
    try:
        from models import base
        print("✓ Models.base imported")
    except ImportError as e:
        print(f"✗ Models.base import failed: {e}")
        return False
    
    try:
        from services import room_service
        print("✓ Services.room_service imported")
    except ImportError as e:
        print(f"✗ Services.room_service import failed: {e}")
        return False
    
    try:
        from utils import validation
        print("✓ Utils.validation imported")
    except ImportError as e:
        print(f"✗ Utils.validation import failed: {e}")
        return False
    
    try:
        from pages import home
        print("✓ Pages.home imported")
    except ImportError as e:
        print(f"✗ Pages.home import failed: {e}")
        return False
    
    print("\n✅ All imports successful!")
    return True


def test_database():
    """Test database initialization."""
    print("\nTesting database...")
    
    try:
        from models import init_db
        init_db()
        print("✓ Database initialized")
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        return False
    
    try:
        from services.data_service import seed_database_if_empty
        seed_database_if_empty()
        print("✓ Database seeded")
    except Exception as e:
        print(f"✗ Database seeding failed: {e}")
        return False
    
    try:
        from services.data_service import get_all_players
        players = get_all_players()
        print(f"✓ Found {len(players)} players in database")
    except Exception as e:
        print(f"✗ Failed to query players: {e}")
        return False
    
    print("\n✅ Database tests passed!")
    return True


def test_services():
    """Test basic service functionality."""
    print("\nTesting services...")
    
    try:
        from services import room_service
        code = room_service.generate_room_code()
        print(f"✓ Generated room code: {code}")
    except Exception as e:
        print(f"✗ Room code generation failed: {e}")
        return False
    
    try:
        from utils.validation import validate_username
        is_valid, msg = validate_username("testuser")
        if is_valid:
            print("✓ Username validation works")
        else:
            print(f"✗ Username validation failed: {msg}")
            return False
    except Exception as e:
        print(f"✗ Validation test failed: {e}")
        return False
    
    print("\n✅ Service tests passed!")
    return True


if __name__ == "__main__":
    print("=" * 50)
    print("IPL Mock Auction Arena - Setup Test")
    print("=" * 50)
    
    all_passed = True
    
    if not test_imports():
        all_passed = False
    
    if not test_database():
        all_passed = False
    
    if not test_services():
        all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Ready to run!")
        print("\nRun the app with: streamlit run app.py")
    else:
        print("❌ SOME TESTS FAILED")
        print("\nPlease fix the errors above before running")
    print("=" * 50)
