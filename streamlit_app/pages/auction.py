"""Auction page for live bidding."""
import streamlit as st
import time
from datetime import datetime
from services import auction_service, team_service, room_service, ai_service
from utils.timer import get_remaining_time, is_timer_expired, format_time
from config import Config


def render():
    """Render the auction page."""
    if not st.session_state.room_code:
        st.error("No room selected. Returning to home...")
        st.session_state.page = 'home'
        st.rerun()
        return
    
    # Get current auction state
    auction_state = auction_service.get_current_auction_state(st.session_state.room_code)
    
    # Check if auction is complete
    if auction_state.auction_complete:
        # Run AI analysis for all teams
        room = room_service.get_room(st.session_state.room_code)
        if room:
            teams = team_service.get_all_teams(st.session_state.room_code)
            for team in teams:
                ai_service.select_playing_xi(team.id)
                ai_service.select_impact_player(team.id)
                ai_service.calculate_team_rating(team.id)
            
            # Update room status
            room.status = 'completed'
        
        st.session_state.page = 'results'
        st.rerun()
        return
    
    st.title(f"⚡ Live Auction - Room: {st.session_state.room_code}")
    
    # Get my team info
    my_team = team_service.get_team(st.session_state.room_code, st.session_state.username)
    if my_team:
        st.session_state.my_purse = my_team.purse_left
    
    # Display purse
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        st.metric("💰 My Purse", f"₹{st.session_state.my_purse:.1f}L")
    with col2:
        if my_team:
            squad_size = len(team_service.get_team_squad(my_team.id))
            st.metric("👥 Squad Size", squad_size)
    
    st.divider()
    
    # Current player display
    if auction_state.current_player:
        player = auction_state.current_player
        
        # Timer
        timer_start = auction_service.get_timer_start(st.session_state.room_code)
        if timer_start:
            remaining = get_remaining_time(timer_start, Config.TIMER_DURATION)
            
            # Display timer
            timer_col1, timer_col2 = st.columns([3, 1])
            with timer_col1:
                st.subheader(f"⏱️ Time Remaining: {format_time(remaining)}")
            with timer_col2:
                if remaining <= 10:
                    st.error("⚠️ HURRY!")
            
            # Check if timer expired
            if is_timer_expired(timer_start, Config.TIMER_DURATION):
                # Handle timer expiry
                result = auction_service.handle_timer_expiry(st.session_state.room_code)
                
                if result:
                    if result['sold_to']:
                        st.success(f"✅ {result['player'].name} sold to {result['sold_to']} for ₹{result['sold_price']:.1f}L!")
                    else:
                        st.info(f"No bids for {result['player'].name}")
                    
                    time.sleep(2)
                
                # Present next player
                next_player = auction_service.present_next_player(st.session_state.room_code)
                if not next_player:
                    # Auction complete
                    st.rerun()
                else:
                    st.rerun()
        
        # Player card
        st.subheader(f"🏏 {player.name}")
        
        player_col1, player_col2, player_col3 = st.columns(3)
        with player_col1:
            st.metric("Role", player.role)
            st.metric("Country", player.country)
        with player_col2:
            st.metric("Base Price", f"₹{player.base_price:.1f}L")
            st.metric("Overseas", "Yes" if player.is_overseas else "No")
        with player_col3:
            st.metric("Batting", f"{player.batting_score:.1f}")
            st.metric("Bowling", f"{player.bowling_score:.1f}")
        
        st.metric("Overall Score", f"{player.overall_score:.1f}", delta=None)
        
        st.divider()
        
        # Current bid info
        st.subheader("💵 Current Bid")
        bid_col1, bid_col2 = st.columns(2)
        with bid_col1:
            st.metric("Amount", f"₹{auction_state.current_bid:.1f}L")
        with bid_col2:
            if auction_state.highest_bidder:
                st.metric("Highest Bidder", auction_state.highest_bidder)
            else:
                st.info("No bids yet")
        
        # Bid button
        next_bid = auction_state.current_bid + Config.BID_INCREMENT
        
        if st.session_state.my_purse >= next_bid:
            if st.button(f"Place Bid (₹{next_bid:.1f}L)", type="primary", use_container_width=True):
                result = auction_service.place_bid(
                    st.session_state.room_code,
                    st.session_state.username
                )
                
                if result.success:
                    st.success(f"✅ Bid placed: ₹{result.new_bid:.1f}L")
                    st.rerun()
                else:
                    st.error(f"❌ {result.message}")
        else:
            st.error(f"❌ Insufficient purse (need ₹{next_bid:.1f}L)")
    
    else:
        st.info("⏳ Waiting for next player...")
        
        # Try to present next player
        next_player = auction_service.present_next_player(st.session_state.room_code)
        if next_player:
            st.rerun()
    
    # Auto-refresh for real-time updates
    if 'last_auction_poll' not in st.session_state:
        st.session_state.last_auction_poll = time.time()
    
    current_time = time.time()
    if current_time - st.session_state.last_auction_poll > 1:  # Poll every second during auction
        st.session_state.last_auction_poll = current_time
        st.rerun()
