"""Results page for auction outcomes."""
import streamlit as st
import pandas as pd
from services import team_service, ai_service, room_service
from models import get_session, Team, TeamRating, TeamPlayer, Player


def render():
    """Render the results page."""
    if not st.session_state.room_code:
        st.error("No room selected. Returning to home...")
        st.session_state.page = 'home'
        st.rerun()
        return
    
    st.title(f"🏆 Auction Results - Room: {st.session_state.room_code}")
    
    # Get winner
    winner = ai_service.determine_winner(st.session_state.room_code)
    
    if winner:
        session = get_session()
        try:
            winner_rating = session.query(TeamRating).filter_by(team_id=winner.id).first()
            
            st.success(f"🎉 **Winner: {winner.team_name}** (Rating: {winner_rating.overall_rating:.2f})")
            st.balloons()
        finally:
            session.close()
    
    st.divider()
    
    # Get all teams
    teams = team_service.get_all_teams(st.session_state.room_code)
    
    if not teams:
        st.warning("No teams found")
        return
    
    # Team ratings comparison
    st.subheader("📊 Team Ratings Comparison")
    
    session = get_session()
    try:
        ratings_data = []
        for team in teams:
            rating = session.query(TeamRating).filter_by(team_id=team.id).first()
            if rating:
                ratings_data.append({
                    'Team': team.team_name,
                    'Overall Rating': rating.overall_rating,
                    'Batting': rating.batting_rating,
                    'Bowling': rating.bowling_rating,
                    'Balance': rating.balance_score
                })
        
        if ratings_data:
            df = pd.DataFrame(ratings_data)
            df = df.sort_values('Overall Rating', ascending=False)
            
            # Bar chart
            st.bar_chart(df.set_index('Team')['Overall Rating'])
            
            # Detailed table
            st.dataframe(df, use_container_width=True, hide_index=True)
    finally:
        session.close()
    
    st.divider()
    
    # Team details
    st.subheader("👥 Team Squads")
    
    for team in teams:
        with st.expander(f"**{team.team_name}** ({team.username})"):
            session = get_session()
            try:
                # Get rating
                rating = session.query(TeamRating).filter_by(team_id=team.id).first()
                
                if rating:
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Overall Rating", f"{rating.overall_rating:.2f}")
                    with col2:
                        st.metric("Batting", f"{rating.batting_rating:.2f}")
                    with col3:
                        st.metric("Bowling", f"{rating.bowling_rating:.2f}")
                    with col4:
                        st.metric("Balance", f"{rating.balance_score:.2f}")
                
                # Get squad
                team_players = session.query(TeamPlayer).filter_by(team_id=team.id).all()
                
                if team_players:
                    # Playing XI
                    st.markdown("**🌟 Playing XI:**")
                    playing_xi = [tp for tp in team_players if tp.in_playing_xi]
                    
                    if playing_xi:
                        xi_data = []
                        for tp in playing_xi:
                            player = session.query(Player).get(tp.player_id)
                            if player:
                                xi_data.append({
                                    'Player': player.name,
                                    'Role': player.role,
                                    'Price': f"₹{tp.price:.1f}L",
                                    'Overall': player.overall_score
                                })
                        
                        st.dataframe(pd.DataFrame(xi_data), use_container_width=True, hide_index=True)
                    else:
                        st.info("Playing XI not selected")
                    
                    # Impact Player
                    impact = [tp for tp in team_players if tp.is_impact_player]
                    if impact:
                        st.markdown("**⚡ Impact Player:**")
                        impact_player = session.query(Player).get(impact[0].player_id)
                        if impact_player:
                            st.success(f"{impact_player.name} ({impact_player.role}) - ₹{impact[0].price:.1f}L")
                    
                    # Bench
                    bench = [tp for tp in team_players if not tp.in_playing_xi]
                    if bench:
                        st.markdown("**🪑 Bench:**")
                        bench_data = []
                        for tp in bench:
                            player = session.query(Player).get(tp.player_id)
                            if player:
                                bench_data.append({
                                    'Player': player.name,
                                    'Role': player.role,
                                    'Price': f"₹{tp.price:.1f}L"
                                })
                        
                        st.dataframe(pd.DataFrame(bench_data), use_container_width=True, hide_index=True)
                    
                    # Purse info
                    st.metric("💰 Purse Remaining", f"₹{team.purse_left:.1f}L")
                else:
                    st.info("No players in squad")
            finally:
                session.close()
    
    st.divider()
    
    # New auction button
    if st.button("🔄 Start New Auction", type="primary"):
        # Reset session state
        st.session_state.room_code = None
        st.session_state.is_host = False
        st.session_state.team_configured = False
        st.session_state.team_name = None
        st.session_state.page = 'home'
        st.rerun()
