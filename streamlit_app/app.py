"""
IPL Mock Auction Arena - Streamlit Application
Main entry point for the application.
"""
import streamlit as st
from config import Config

# Page configuration
st.set_page_config(
    page_title="IPL Mock Auction Arena",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)


def init_database():
    """Initialize database connection and create tables if needed."""
    from models import init_db
    from services.data_service import seed_database_if_empty
    
    # Create tables
    init_db()
    
    # Seed database with players if empty
    seed_database_if_empty()


def init_session_state():
    """Initialize Streamlit session state variables."""
    # User information
    if 'username' not in st.session_state:
        st.session_state.username = None
    
    if 'room_code' not in st.session_state:
        st.session_state.room_code = None
    
    if 'is_host' not in st.session_state:
        st.session_state.is_host = False
    
    # Navigation
    if 'page' not in st.session_state:
        st.session_state.page = 'home'
    
    # Team configuration
    if 'team_configured' not in st.session_state:
        st.session_state.team_configured = False
    
    if 'team_name' not in st.session_state:
        st.session_state.team_name = None
    
    if 'team_logo' not in st.session_state:
        st.session_state.team_logo = None
    
    if 'initial_purse' not in st.session_state:
        st.session_state.initial_purse = 100.0
    
    # Auction state
    if 'current_player_id' not in st.session_state:
        st.session_state.current_player_id = None
    
    if 'current_bid' not in st.session_state:
        st.session_state.current_bid = None
    
    if 'highest_bidder' not in st.session_state:
        st.session_state.highest_bidder = None
    
    if 'timer_start' not in st.session_state:
        st.session_state.timer_start = None
    
    if 'my_purse' not in st.session_state:
        st.session_state.my_purse = 100.0
    
    # Polling
    if 'last_poll' not in st.session_state:
        st.session_state.last_poll = 0


def render_navigation():
    """Render sidebar navigation."""
    with st.sidebar:
        st.title("🏏 IPL Auction")
        
        # Show current user info if logged in
        if st.session_state.username:
            st.success(f"👤 {st.session_state.username}")
            
            if st.session_state.room_code:
                st.info(f"🚪 Room: {st.session_state.room_code}")
        
        st.divider()
        
        # Navigation menu
        if st.session_state.username and st.session_state.room_code:
            # Show navigation options when in a room
            page = st.radio(
                "Navigate",
                options=['lobby', 'auction', 'results'],
                format_func=lambda x: {
                    'lobby': '🏠 Lobby',
                    'auction': '⚡ Auction',
                    'results': '🏆 Results'
                }[x],
                key='nav_radio'
            )
            
            if page != st.session_state.page:
                st.session_state.page = page
                st.rerun()
        else:
            st.info("Please create or join a room to start")


def main():
    """Main application loop."""
    # Initialize database
    init_database()
    
    # Initialize session state
    init_session_state()
    
    # Render navigation
    render_navigation()
    
    # Route to appropriate page
    if st.session_state.page == 'home':
        from pages import home
        home.render()
    elif st.session_state.page == 'lobby':
        from pages import lobby
        lobby.render()
    elif st.session_state.page == 'auction':
        from pages import auction
        auction.render()
    elif st.session_state.page == 'results':
        from pages import results
        results.render()
    else:
        st.error("Invalid page")


if __name__ == "__main__":
    main()
