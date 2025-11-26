"""Home page for IPL Mock Auction Arena."""
import streamlit as st
from services import room_service
from utils.validation import validate_username, validate_room_code


def render():
    """Render the home page."""
    st.title("🏏 IPL Mock Auction Arena")
    st.markdown("### Welcome to the ultimate IPL player auction experience!")
    
    st.divider()
    
    # Username input
    st.subheader("👤 Enter Your Username")
    username = st.text_input(
        "Username",
        value=st.session_state.username if st.session_state.username else "",
        placeholder="Enter your username",
        key="username_input"
    )
    
    if username:
        is_valid, message = validate_username(username)
        if not is_valid:
            st.error(message)
        else:
            st.session_state.username = username.strip()
    
    st.divider()
    
    # Only show room options if username is valid
    if st.session_state.username:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🆕 Create New Room")
            st.markdown("Start a new auction and invite friends!")
            
            if st.button("Create Room", type="primary", use_container_width=True):
                try:
                    room = room_service.create_room(st.session_state.username)
                    st.session_state.room_code = room.code
                    st.session_state.is_host = True
                    st.session_state.page = 'lobby'
                    st.success(f"✅ Room created! Code: **{room.code}**")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error creating room: {str(e)}")
        
        with col2:
            st.subheader("🚪 Join Existing Room")
            st.markdown("Enter the room code to join!")
            
            room_code_input = st.text_input(
                "Room Code",
                placeholder="Enter 6-character code",
                max_chars=6,
                key="room_code_input"
            ).upper()
            
            if st.button("Join Room", type="secondary", use_container_width=True):
                if not room_code_input:
                    st.error("Please enter a room code")
                else:
                    is_valid, message = validate_room_code(room_code_input)
                    if not is_valid:
                        st.error(message)
                    else:
                        try:
                            success, message, user = room_service.join_room(
                                room_code_input,
                                st.session_state.username
                            )
                            
                            if success:
                                st.session_state.room_code = room_code_input
                                st.session_state.is_host = False
                                st.session_state.page = 'lobby'
                                st.success(f"✅ {message}")
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")
                        except Exception as e:
                            st.error(f"Error joining room: {str(e)}")
    else:
        st.info("👆 Please enter your username to continue")
    
    st.divider()
    
    # Instructions
    with st.expander("📖 How to Play"):
        st.markdown("""
        **Welcome to IPL Mock Auction Arena!**
        
        1. **Enter your username** to get started
        2. **Create a room** or **join an existing room** with a code
        3. **Configure your team** in the lobby (name, logo, starting purse)
        4. **Wait for all participants** to join (2-10 players required)
        5. **Host starts the auction** when everyone is ready
        6. **Bid on players** during the auction (60 seconds per player)
        7. **View results** with AI-powered team ratings and playing XI selection
        
        **Features:**
        - Real-time multiplayer bidding
        - 100+ IPL players with detailed stats
        - Automatic playing XI selection
        - Team rating and analysis
        - Impact player selection
        """)
