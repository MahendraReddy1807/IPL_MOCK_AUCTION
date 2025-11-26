"""Lobby page for team configuration."""
import streamlit as st
import time
from services import room_service, team_service, auction_service
from utils.validation import validate_team_name, validate_purse
from config import Config


def render():
    """Render the lobby page."""
    if not st.session_state.room_code:
        st.error("No room selected. Returning to home...")
        st.session_state.page = 'home'
        st.rerun()
        return
    
    st.title(f"🏠 Lobby - Room: {st.session_state.room_code}")
    
    # Get room info
    room = room_service.get_room(st.session_state.room_code)
    if not room:
        st.error("Room not found!")
        return
    
    # Display participants
    st.subheader("👥 Participants")
    participants = room_service.get_room_participants(st.session_state.room_code)
    
    cols = st.columns(min(len(participants), 5))
    for idx, user in enumerate(participants):
        with cols[idx % 5]:
            if user.username == room.host_username:
                st.success(f"👑 {user.username}")
            else:
                st.info(f"👤 {user.username}")
    
    st.caption(f"{len(participants)}/{room.max_users} players ({room.min_users} minimum required)")
    
    st.divider()
    
    # Team configuration
    st.subheader("⚙️ Configure Your Team")
    
    with st.form("team_config_form"):
        team_name = st.text_input(
            "Team Name",
            value=st.session_state.team_name if st.session_state.team_name else "",
            placeholder="Enter your team name"
        )
        
        purse = st.number_input(
            "Starting Purse (Lakhs)",
            min_value=50.0,
            max_value=200.0,
            value=st.session_state.initial_purse,
            step=5.0
        )
        
        logo = st.file_uploader(
            "Team Logo (Optional)",
            type=['png', 'jpg', 'jpeg', 'gif']
        )
        
        submitted = st.form_submit_button("Save Team Configuration", type="primary")
        
        if submitted:
            # Validate inputs
            is_valid_name, name_message = validate_team_name(team_name)
            is_valid_purse, purse_message = validate_purse(purse)
            
            if not is_valid_name:
                st.error(name_message)
            elif not is_valid_purse:
                st.error(purse_message)
            else:
                # Save logo if uploaded
                logo_url = None
                if logo:
                    success, message, logo_url = team_service.save_logo(logo)
                    if not success:
                        st.error(message)
                        logo_url = None
                
                # Configure team
                success, message, team = team_service.configure_team(
                    room.id,
                    st.session_state.username,
                    team_name,
                    purse,
                    logo_url
                )
                
                if success:
                    st.session_state.team_configured = True
                    st.session_state.team_name = team_name
                    st.session_state.initial_purse = purse
                    st.success(f"✅ {message}")
                    st.rerun()
                else:
                    st.error(f"❌ {message}")
    
    if st.session_state.team_configured:
        st.success(f"✅ Team configured: **{st.session_state.team_name}**")
    
    st.divider()
    
    # Start auction button (host only)
    if st.session_state.is_host:
        st.subheader("🚀 Start Auction")
        
        # Check if all participants have configured teams
        all_teams = team_service.get_all_teams(st.session_state.room_code)
        configured_count = len(all_teams)
        
        st.info(f"{configured_count}/{len(participants)} teams configured")
        
        if len(participants) < room.min_users:
            st.warning(f"⚠️ Need at least {room.min_users} participants to start")
        elif configured_count < len(participants):
            st.warning("⚠️ All participants must configure their teams first")
        else:
            if st.button("Start Auction", type="primary", use_container_width=True):
                # Start auction
                success, message = room_service.start_auction(
                    st.session_state.room_code,
                    st.session_state.username
                )
                
                if success:
                    # Initialize auction
                    auction_service.initialize_auction(st.session_state.room_code)
                    
                    # Present first player
                    first_player = auction_service.present_next_player(st.session_state.room_code)
                    
                    if first_player:
                        st.session_state.page = 'auction'
                        st.success("✅ Auction started!")
                        st.rerun()
                    else:
                        st.error("No players available for auction")
                else:
                    st.error(f"❌ {message}")
    else:
        st.info("⏳ Waiting for host to start the auction...")
    
    # Auto-refresh for participant updates
    if 'last_lobby_poll' not in st.session_state:
        st.session_state.last_lobby_poll = time.time()
    
    current_time = time.time()
    if current_time - st.session_state.last_lobby_poll > Config.POLL_INTERVAL:
        st.session_state.last_lobby_poll = current_time
        
        # Check if auction has started
        room = room_service.get_room(st.session_state.room_code)
        if room and room.status == 'active':
            st.session_state.page = 'auction'
            st.rerun()
