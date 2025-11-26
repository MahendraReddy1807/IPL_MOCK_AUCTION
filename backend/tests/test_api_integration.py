"""Integration tests for REST API endpoints."""
import pytest
import json
import io
from app.models.player import Player
from app.models.room import Room
from app.models.team import Team
from app.models.team_player import TeamPlayer
from app.models.team_rating import TeamRating
from app import db


class TestRoomCreationAndJoining:
    """Test room creation and joining flow."""
    
    def test_create_room_success(self, client):
        """Test successful room creation."""
        response = client.post('/api/rooms/create', 
                              json={'host_username': 'testuser'})
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'room_code' in data
        assert data['host_username'] == 'testuser'
        assert data['status'] == 'lobby'
    
    def test_create_room_empty_username(self, client):
        """Test room creation with empty username."""
        response = client.post('/api/rooms/create', 
                              json={'host_username': ''})
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] is True
        assert 'Username cannot be empty' in data['message']
    
    def test_join_room_success(self, client):
        """Test successful room joining."""
        # Create room first
        create_response = client.post('/api/rooms/create', 
                                     json={'host_username': 'host'})
        room_code = json.loads(create_response.data)['room_code']
        
        # Join room
        response = client.post('/api/rooms/join', 
                              json={'room_code': room_code, 'username': 'player1'})
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['room_code'] == room_code
        assert data['username'] == 'player1'
        assert 'host' in data['participants']
        assert 'player1' in data['participants']
    
    def test_join_nonexistent_room(self, client):
        """Test joining a room that doesn't exist."""
        response = client.post('/api/rooms/join', 
                              json={'room_code': 'INVALID', 'username': 'player1'})
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] is True
    
    def test_join_room_empty_username(self, client):
        """Test joining room with empty username."""
        # Create room first
        create_response = client.post('/api/rooms/create', 
                                     json={'host_username': 'host'})
        room_code = json.loads(create_response.data)['room_code']
        
        # Try to join with empty username
        response = client.post('/api/rooms/join', 
                              json={'room_code': room_code, 'username': ''})
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] is True
        assert 'Username cannot be empty' in data['message']
    
    def test_get_room_details(self, client):
        """Test getting room details."""
        # Create room
        create_response = client.post('/api/rooms/create', 
                                     json={'host_username': 'host'})
        room_code = json.loads(create_response.data)['room_code']
        
        # Get room details
        response = client.get(f'/api/rooms/{room_code}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['room_code'] == room_code
        assert data['status'] == 'lobby'
        assert data['host_username'] == 'host'
        assert data['min_users'] == 5
        assert data['max_users'] == 10
        assert len(data['participants']) == 1
    
    def test_get_nonexistent_room(self, client):
        """Test getting details of nonexistent room."""
        response = client.get('/api/rooms/INVALID')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['error'] is True
        assert 'Room not found' in data['message']


class TestTeamConfiguration:
    """Test team configuration flow."""
    
    def test_configure_team_success(self, client, app):
        """Test successful team configuration."""
        # Create room and join
        create_response = client.post('/api/rooms/create', 
                                     json={'host_username': 'host'})
        room_code = json.loads(create_response.data)['room_code']
        
        # Configure team
        response = client.post('/api/teams/configure', json={
            'room_code': room_code,
            'username': 'host',
            'team_name': 'Test Team',
            'logo_url': '/logos/test.png',
            'purse': 100.0
        })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['team_name'] == 'Test Team'
        assert data['logo_url'] == '/logos/test.png'
        assert data['purse'] == 100.0
    
    def test_configure_team_empty_name(self, client):
        """Test team configuration with empty name."""
        # Create room
        create_response = client.post('/api/rooms/create', 
                                     json={'host_username': 'host'})
        room_code = json.loads(create_response.data)['room_code']
        
        # Try to configure with empty name
        response = client.post('/api/teams/configure', json={
            'room_code': room_code,
            'username': 'host',
            'team_name': '',
            'purse': 100.0
        })
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] is True
        assert 'Team name cannot be empty' in data['message']
    
    def test_configure_team_invalid_purse(self, client):
        """Test team configuration with invalid purse."""
        # Create room
        create_response = client.post('/api/rooms/create', 
                                     json={'host_username': 'host'})
        room_code = json.loads(create_response.data)['room_code']
        
        # Try to configure with negative purse
        response = client.post('/api/teams/configure', json={
            'room_code': room_code,
            'username': 'host',
            'team_name': 'Test Team',
            'purse': -10.0
        })
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] is True
        assert 'Purse must be a positive number' in data['message']
    
    def test_configure_team_nonexistent_room(self, client):
        """Test team configuration for nonexistent room."""
        response = client.post('/api/teams/configure', json={
            'room_code': 'INVALID',
            'username': 'host',
            'team_name': 'Test Team',
            'purse': 100.0
        })
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['error'] is True
        assert 'Room not found' in data['message']
    
    def test_upload_logo_success(self, client):
        """Test successful logo upload."""
        # Create a fake image file
        data = {
            'logo': (io.BytesIO(b"fake image data"), 'test.png')
        }
        
        response = client.post('/api/teams/upload-logo',
                              data=data,
                              content_type='multipart/form-data')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'logo_url' in data
        assert 'test.png' in data['logo_url']
    
    def test_upload_logo_no_file(self, client):
        """Test logo upload without file."""
        response = client.post('/api/teams/upload-logo',
                              data={},
                              content_type='multipart/form-data')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] is True
        assert 'No file provided' in data['message']
    
    def test_upload_logo_invalid_type(self, client):
        """Test logo upload with invalid file type."""
        data = {
            'logo': (io.BytesIO(b"fake data"), 'test.txt')
        }
        
        response = client.post('/api/teams/upload-logo',
                              data=data,
                              content_type='multipart/form-data')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] is True
        assert 'Invalid file type' in data['message']


class TestPlayerRetrieval:
    """Test player retrieval."""
    
    def test_get_players_empty(self, client):
        """Test getting players when database is empty."""
        response = client.get('/api/players')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'players' in data
        assert len(data['players']) == 0
    
    def test_get_players_with_data(self, client, app):
        """Test getting players with data in database."""
        # Add some test players
        with app.app_context():
            player1 = Player(
                name='Test Player 1',
                role='BAT',
                country='India',
                base_price=1.0,
                batting_score=80.0,
                bowling_score=20.0,
                overall_score=75.0,
                is_overseas=False
            )
            player2 = Player(
                name='Test Player 2',
                role='BOWL',
                country='Australia',
                base_price=2.0,
                batting_score=30.0,
                bowling_score=85.0,
                overall_score=70.0,
                is_overseas=True
            )
            db.session.add(player1)
            db.session.add(player2)
            db.session.commit()
        
        response = client.get('/api/players')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'players' in data
        assert len(data['players']) == 2
        assert data['players'][0]['name'] == 'Test Player 1'
        assert data['players'][1]['name'] == 'Test Player 2'


class TestAuctionState:
    """Test auction state retrieval."""
    
    def test_get_auction_state_no_current_player(self, client, app):
        """Test getting auction state when no player is being auctioned."""
        # Create room
        create_response = client.post('/api/rooms/create', 
                                     json={'host_username': 'host'})
        room_code = json.loads(create_response.data)['room_code']
        
        response = client.get(f'/api/auction/{room_code}/state')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['room_code'] == room_code
        assert data['current_player'] is None
        assert data['auction_complete'] is False


class TestResults:
    """Test results retrieval."""
    
    def test_get_results_nonexistent_room(self, client):
        """Test getting results for nonexistent room."""
        response = client.get('/api/results/INVALID')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['error'] is True
        assert 'Room not found' in data['message']
    
    def test_get_results_empty_auction(self, client, app):
        """Test getting results for auction with no teams."""
        # Create room
        create_response = client.post('/api/rooms/create', 
                                     json={'host_username': 'host'})
        room_code = json.loads(create_response.data)['room_code']
        
        response = client.get(f'/api/results/{room_code}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['room_code'] == room_code
        assert len(data['teams']) == 0
        assert data['winner'] is None
    
    def test_get_results_with_teams(self, client, app):
        """Test getting results with teams and players."""
        # Create room
        create_response = client.post('/api/rooms/create', 
                                     json={'host_username': 'host'})
        room_code = json.loads(create_response.data)['room_code']
        
        with app.app_context():
            # Get room
            room = Room.query.filter_by(code=room_code).first()
            
            # Create team
            team = Team(
                room_id=room.id,
                username='host',
                team_name='Test Team',
                logo_url='/logos/test.png',
                initial_purse=100.0,
                purse_left=80.0
            )
            db.session.add(team)
            db.session.commit()
            
            # Create player
            player = Player(
                name='Test Player',
                role='BAT',
                country='India',
                base_price=1.0,
                batting_score=80.0,
                bowling_score=20.0,
                overall_score=75.0,
                is_overseas=False
            )
            db.session.add(player)
            db.session.commit()
            
            # Add player to team
            team_player = TeamPlayer(
                team_id=team.id,
                player_id=player.id,
                price=20.0,
                in_playing_xi=True,
                is_impact_player=False
            )
            db.session.add(team_player)
            
            # Add team rating
            rating = TeamRating(
                team_id=team.id,
                overall_rating=85.0,
                batting_rating=80.0,
                bowling_rating=70.0,
                balance_score=75.0,
                bench_depth=60.0,
                role_coverage=80.0
            )
            db.session.add(rating)
            db.session.commit()
        
        response = client.get(f'/api/results/{room_code}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['room_code'] == room_code
        assert len(data['teams']) == 1
        assert data['teams'][0]['team_name'] == 'Test Team'
        assert len(data['teams'][0]['squad']) == 1
        assert len(data['teams'][0]['playing_xi']) == 1
        assert data['teams'][0]['rating']['overall_rating'] == 85.0


class TestCORS:
    """Test CORS configuration."""
    
    def test_cors_headers_present(self, client):
        """Test that CORS headers are present in responses."""
        response = client.get('/api/players')
        
        # CORS headers should be present
        assert 'Access-Control-Allow-Origin' in response.headers
