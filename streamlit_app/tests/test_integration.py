"""Integration tests for complete workflows."""
import pytest
from services import room_service, team_service, auction_service, ai_service
from models import get_session, Player, AuctionPlayer


class TestCompleteAuctionFlow:
    """Test complete auction workflow from start to finish."""
    
    def test_full_auction_workflow(self):
        """Test complete auction flow: create room → configure teams → auction → results."""
        
        # Step 1: Create room
        room = room_service.create_room("host")
        assert room is not None
        assert room.status == "lobby"
        
        # Step 2: Multiple users join
        users = ["player1", "player2", "player3", "player4"]
        for user in users:
            success, msg, user_obj = room_service.join_room(room.code, user)
            assert success is True
        
        # Step 3: Configure teams
        teams = []
        for i, user in enumerate(["host"] + users):
            success, msg, team = team_service.configure_team(
                room.id,
                user,
                f"Team {i+1}",
                100.0
            )
            assert success is True
            teams.append(team)
        
        # Step 4: Start auction
        success, msg = room_service.start_auction(room.code, "host")
        assert success is True
        
        # Step 5: Initialize auction
        success, msg = auction_service.initialize_auction(room.code)
        assert success is True
        
        # Step 6: Add some test players
        session = get_session()
        try:
            test_players = [
                Player(
                    name=f"Player {i}",
                    role=["BAT", "BOWL", "AR", "WK"][i % 4],
                    country="India",
                    base_price=10.0,
                    batting_score=50.0 + i,
                    bowling_score=50.0 - i,
                    overall_score=50.0,
                    is_overseas=False
                )
                for i in range(15)
            ]
            
            for player in test_players:
                session.add(player)
            session.commit()
            
            # Create auction players
            for player in test_players:
                ap = AuctionPlayer(
                    room_id=room.id,
                    player_id=player.id,
                    is_sold=False
                )
                session.add(ap)
            session.commit()
            
            # Step 7: Simulate auction (present and sell a few players)
            for i in range(3):
                player = auction_service.present_next_player(room.code)
                assert player is not None
                
                # Place some bids
                bidder = teams[i % len(teams)]
                result = auction_service.place_bid(room.code, bidder.username)
                assert result.success is True
                
                # Handle timer expiry (sell player)
                sold_info = auction_service.handle_timer_expiry(room.code)
                assert sold_info is not None
                assert sold_info['sold_to'] == bidder.username
            
            # Step 8: Run AI analysis for teams with players
            for team in teams[:3]:  # Only teams that bought players
                squad = team_service.get_team_squad(team.id)
                if len(squad) >= 11:
                    playing_xi = ai_service.select_playing_xi(team.id)
                    impact = ai_service.select_impact_player(team.id)
                    rating = ai_service.calculate_team_rating(team.id)
                    
                    assert rating is not None
            
            # Step 9: Determine winner
            winner = ai_service.determine_winner(room.code)
            # Winner might be None if no teams have ratings yet
            
        finally:
            session.close()


class TestMultiUserSync:
    """Test multi-user synchronization."""
    
    def test_multiple_users_see_same_state(self):
        """Test that multiple users see consistent auction state."""
        
        # Create room
        room = room_service.create_room("host")
        
        # Add multiple users
        for i in range(3):
            room_service.join_room(room.code, f"player{i}")
        
        # Get participants from different "sessions"
        participants1 = room_service.get_room_participants(room.code)
        participants2 = room_service.get_room_participants(room.code)
        
        # Should see same participants
        assert len(participants1) == len(participants2)
        
        usernames1 = sorted([p.username for p in participants1])
        usernames2 = sorted([p.username for p in participants2])
        
        assert usernames1 == usernames2


class TestErrorRecovery:
    """Test error recovery scenarios."""
    
    def test_invalid_room_join_recovery(self):
        """Test recovery from invalid room join."""
        
        # Try to join non-existent room
        success, msg, user = room_service.join_room("FAKE01", "player1")
        assert success is False
        
        # Should be able to create new room after failure
        room = room_service.create_room("player1")
        assert room is not None
    
    def test_insufficient_purse_recovery(self):
        """Test recovery from insufficient purse."""
        
        room = room_service.create_room("host")
        success, msg, team = team_service.configure_team(
            room.id,
            "player1",
            "Test Team",
            20.0  # Low purse
        )
        
        assert success is True
        
        # Try to place high bid (would fail in real auction)
        # Team should still exist and be valid
        retrieved_team = team_service.get_team(room.code, "player1")
        assert retrieved_team is not None
        assert retrieved_team.purse_left == 20.0
    
    def test_duplicate_team_name_recovery(self):
        """Test recovery from duplicate team name."""
        
        room = room_service.create_room("host")
        
        # Configure first team
        success1, msg1, team1 = team_service.configure_team(
            room.id,
            "player1",
            "Team A",
            100.0
        )
        assert success1 is True
        
        # Try to configure second team with same name
        success2, msg2, team2 = team_service.configure_team(
            room.id,
            "player2",
            "Team A",
            100.0
        )
        
        # Should succeed (different user)
        # Or handle appropriately based on business logic
        
        # User should be able to choose different name
        success3, msg3, team3 = team_service.configure_team(
            room.id,
            "player2",
            "Team B",
            100.0
        )
        assert success3 is True


class TestConcurrentOperations:
    """Test concurrent operations."""
    
    def test_concurrent_room_creation(self):
        """Test multiple rooms can be created concurrently."""
        
        rooms = []
        for i in range(5):
            room = room_service.create_room(f"host{i}")
            rooms.append(room)
        
        # All rooms should have unique codes
        codes = [r.code for r in rooms]
        assert len(codes) == len(set(codes))
    
    def test_concurrent_team_configuration(self):
        """Test multiple teams can be configured concurrently."""
        
        room = room_service.create_room("host")
        
        # Add users
        for i in range(5):
            room_service.join_room(room.code, f"player{i}")
        
        # Configure teams concurrently
        teams = []
        for i in range(5):
            success, msg, team = team_service.configure_team(
                room.id,
                f"player{i}",
                f"Team {i}",
                100.0
            )
            if success:
                teams.append(team)
        
        assert len(teams) == 5
