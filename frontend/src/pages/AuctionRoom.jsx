import React, { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { auctionAPI } from '../services/api'
import socketService from '../services/socket'

function AuctionRoom() {
  const { roomCode } = useParams()
  const navigate = useNavigate()
  
  // State management
  const [username, setUsername] = useState('')
  const [currentPlayer, setCurrentPlayer] = useState(null)
  const [currentBid, setCurrentBid] = useState(0)
  const [highestBidder, setHighestBidder] = useState(null)
  const [timeRemaining, setTimeRemaining] = useState(30)
  const [bidHistory, setBidHistory] = useState([])
  const [teams, setTeams] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [bidError, setBidError] = useState('')
  const [auctionComplete, setAuctionComplete] = useState(false)
  
  const timerRef = useRef(null)
  const timerStartRef = useRef(null)

  // Load username and initial state on mount
  useEffect(() => {
    const storedUsername = localStorage.getItem('username')
    const storedRoomCode = localStorage.getItem('roomCode')
    
    if (!storedUsername || storedRoomCode !== roomCode) {
      navigate('/')
      return
    }
    
    setUsername(storedUsername)
    loadInitialState()
  }, [roomCode, navigate])

  // Set up Socket.IO connection and event listeners
  useEffect(() => {
    if (!username) return

    const socket = socketService.connect()
    
    // Join the room
    socketService.emit('join_room', {
      room_code: roomCode,
      username: username
    })

    // Request current auction state
    socketService.emit('get_auction_state', {
      room_code: roomCode
    })

    // Listen for player presented event
    const handlePlayerPresented = (data) => {
      console.log('Player presented:', data)
      setCurrentPlayer(data.player)
      setCurrentBid(data.current_bid)
      setHighestBidder(null)
      setTimeRemaining(data.timer_duration || 30)
      timerStartRef.current = Date.now()
      setBidError('')
      
      // Add to bid history
      setBidHistory(prev => [{
        type: 'new_player',
        player: data.player.name,
        timestamp: new Date().toLocaleTimeString()
      }, ...prev])
    }

    // Listen for bid placed event
    const handleBidPlaced = (data) => {
      console.log('Bid placed:', data)
      setCurrentBid(data.current_highest)
      setHighestBidder(data.highest_bidder)
      setBidError('')
      
      // Add to bid history
      setBidHistory(prev => [{
        type: 'bid',
        username: data.username,
        amount: data.bid_amount,
        timestamp: new Date().toLocaleTimeString()
      }, ...prev])
    }

    // Listen for player sold event
    const handlePlayerSold = (data) => {
      console.log('Player sold:', data)
      
      // Add to bid history
      setBidHistory(prev => [{
        type: 'sold',
        player: data.player.name,
        soldTo: data.sold_to,
        price: data.sold_price,
        timestamp: new Date().toLocaleTimeString()
      }, ...prev])
      
      // Update team squad size
      setTeams(prevTeams => 
        prevTeams.map(team => 
          team.username === data.sold_to
            ? { ...team, squad_size: (team.squad_size || 0) + 1 }
            : team
        )
      )
    }

    // Listen for purse updated event
    const handlePurseUpdated = (data) => {
      console.log('Purse updated:', data)
      
      // Update team purse
      setTeams(prevTeams => 
        prevTeams.map(team => 
          team.username === data.username
            ? { ...team, purse_left: data.new_purse }
            : team
        )
      )
    }

    // Listen for auction completed event
    const handleAuctionCompleted = (data) => {
      console.log('Auction completed:', data)
      setAuctionComplete(true)
      
      // Add to bid history
      setBidHistory(prev => [{
        type: 'completed',
        message: data.message,
        timestamp: new Date().toLocaleTimeString()
      }, ...prev])
      
      // Navigate to results after a delay
      setTimeout(() => {
        navigate(`/results/${roomCode}`)
      }, 3000)
    }

    // Listen for auction state response
    const handleAuctionState = (data) => {
      console.log('Auction state:', data)
      if (data.current_player) {
        setCurrentPlayer(data.current_player)
        setCurrentBid(data.current_bid)
        setHighestBidder(data.highest_bidder)
        setTimeRemaining(data.timer_remaining || 30)
        timerStartRef.current = Date.now()
      }
      if (data.auction_complete) {
        setAuctionComplete(true)
      }
    }

    // Listen for bid error
    const handleBidError = (data) => {
      console.log('Bid error:', data)
      setBidError(data.message)
      setTimeout(() => setBidError(''), 3000)
    }

    socketService.on('player_presented', handlePlayerPresented)
    socketService.on('bid_placed', handleBidPlaced)
    socketService.on('player_sold', handlePlayerSold)
    socketService.on('purse_updated', handlePurseUpdated)
    socketService.on('auction_completed', handleAuctionCompleted)
    socketService.on('auction_state', handleAuctionState)
    socketService.on('bid_error', handleBidError)

    // Cleanup on unmount
    return () => {
      socketService.off('player_presented', handlePlayerPresented)
      socketService.off('bid_placed', handleBidPlaced)
      socketService.off('player_sold', handlePlayerSold)
      socketService.off('purse_updated', handlePurseUpdated)
      socketService.off('auction_completed', handleAuctionCompleted)
      socketService.off('auction_state', handleAuctionState)
      socketService.off('bid_error', handleBidError)
    }
  }, [username, roomCode, navigate])

  // Timer countdown effect
  useEffect(() => {
    if (!currentPlayer || auctionComplete) return

    timerRef.current = setInterval(() => {
      const elapsed = Math.floor((Date.now() - timerStartRef.current) / 1000)
      const remaining = Math.max(0, 30 - elapsed)
      setTimeRemaining(remaining)

      if (remaining === 0) {
        clearInterval(timerRef.current)
        // Emit timer expired event
        socketService.emit('timer_expired', {
          room_code: roomCode
        })
      }
    }, 100)

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current)
      }
    }
  }, [currentPlayer, roomCode, auctionComplete])

  const loadInitialState = async () => {
    try {
      const response = await auctionAPI.getAuctionState(roomCode)
      const data = response.data
      
      // Load teams data
      if (data.teams) {
        setTeams(data.teams)
      }
      
      setLoading(false)
    } catch (err) {
      console.error('Failed to load auction state:', err)
      setError(err.response?.data?.message || 'Failed to load auction state')
      setLoading(false)
    }
  }

  const handlePlaceBid = () => {
    if (!currentPlayer || auctionComplete) return
    
    setBidError('')
    
    // Emit place bid event
    socketService.emit('place_bid', {
      room_code: roomCode,
      username: username
    })
  }

  const getRoleColor = (role) => {
    const colors = {
      'BAT': 'bg-blue-500',
      'BOWL': 'bg-red-500',
      'AR': 'bg-green-500',
      'WK': 'bg-yellow-500'
    }
    return colors[role] || 'bg-gray-500'
  }

  const getRoleIcon = (role) => {
    const icons = {
      'BAT': '🏏',
      'BOWL': '⚡',
      'AR': '⭐',
      'WK': '🧤'
    }
    return icons[role] || '👤'
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading auction room...</div>
      </div>
    )
  }

  if (error && !currentPlayer) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 flex items-center justify-center px-4">
        <div className="bg-white rounded-lg shadow-2xl p-8 max-w-md w-full">
          <div className="text-red-600 text-center mb-4">
            <svg className="w-16 h-16 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h2 className="text-2xl font-bold mb-2">Error</h2>
            <p>{error}</p>
          </div>
          <button
            onClick={() => navigate('/')}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-4 rounded-lg transition duration-200"
          >
            Back to Home
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 py-4 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-4">
          <h1 className="text-3xl font-bold text-white mb-2">🏏 IPL Auction Arena</h1>
          <div className="inline-block bg-white rounded-lg px-4 py-2 shadow-lg">
            <p className="text-sm text-gray-600">Room: <span className="font-bold text-blue-600">{roomCode}</span></p>
          </div>
        </div>

        {/* Auction Complete Message */}
        {auctionComplete && (
          <div className="mb-4 p-4 bg-green-100 border border-green-400 text-green-700 rounded-lg text-center">
            <h2 className="text-2xl font-bold mb-2">🎉 Auction Complete!</h2>
            <p>Redirecting to results...</p>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
          {/* Main Auction Area - Left Side */}
          <div className="lg:col-span-3 space-y-4">
            {/* Current Player Card */}
            {currentPlayer ? (
              <div className="bg-white rounded-lg shadow-2xl p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center mb-2">
                      <span className={`${getRoleColor(currentPlayer.role)} text-white px-3 py-1 rounded-full text-sm font-bold mr-3`}>
                        {getRoleIcon(currentPlayer.role)} {currentPlayer.role}
                      </span>
                      {currentPlayer.is_overseas && (
                        <span className="bg-purple-500 text-white px-3 py-1 rounded-full text-sm font-bold">
                          🌍 Overseas
                        </span>
                      )}
                    </div>
                    <h2 className="text-3xl font-bold text-gray-800 mb-1">{currentPlayer.name}</h2>
                    <p className="text-gray-600 text-lg">{currentPlayer.country}</p>
                  </div>
                  
                  {/* Timer */}
                  <div className="text-center">
                    <div className={`text-5xl font-bold ${timeRemaining <= 10 ? 'text-red-600 animate-pulse' : 'text-blue-600'}`}>
                      {timeRemaining}
                    </div>
                    <p className="text-sm text-gray-600 mt-1">seconds</p>
                  </div>
                </div>

                {/* Player Stats */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                  <div className="bg-blue-50 rounded-lg p-3 text-center">
                    <p className="text-sm text-gray-600 mb-1">Base Price</p>
                    <p className="text-xl font-bold text-blue-600">₹{currentPlayer.base_price}L</p>
                  </div>
                  <div className="bg-green-50 rounded-lg p-3 text-center">
                    <p className="text-sm text-gray-600 mb-1">Batting</p>
                    <p className="text-xl font-bold text-green-600">{currentPlayer.batting_score?.toFixed(1) || 'N/A'}</p>
                  </div>
                  <div className="bg-red-50 rounded-lg p-3 text-center">
                    <p className="text-sm text-gray-600 mb-1">Bowling</p>
                    <p className="text-xl font-bold text-red-600">{currentPlayer.bowling_score?.toFixed(1) || 'N/A'}</p>
                  </div>
                  <div className="bg-purple-50 rounded-lg p-3 text-center">
                    <p className="text-sm text-gray-600 mb-1">Overall</p>
                    <p className="text-xl font-bold text-purple-600">{currentPlayer.overall_score?.toFixed(1) || 'N/A'}</p>
                  </div>
                </div>

                {/* Current Bid Section */}
                <div className="bg-gradient-to-r from-yellow-400 to-orange-500 rounded-lg p-6 mb-4">
                  <div className="text-center">
                    <p className="text-white text-lg mb-2">Current Bid</p>
                    <p className="text-white text-5xl font-bold mb-2">₹{currentBid}L</p>
                    {highestBidder && (
                      <p className="text-white text-lg">
                        Highest Bidder: <span className="font-bold">{highestBidder}</span>
                        {highestBidder === username && ' (You!)'}
                      </p>
                    )}
                  </div>
                </div>

                {/* Bid Button */}
                {bidError && (
                  <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-lg text-center">
                    {bidError}
                  </div>
                )}
                
                <button
                  onClick={handlePlaceBid}
                  disabled={auctionComplete || timeRemaining === 0}
                  className="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-4 px-6 rounded-lg text-xl transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
                >
                  {auctionComplete ? 'Auction Complete' : timeRemaining === 0 ? 'Time Up!' : '💰 Place Bid'}
                </button>
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow-2xl p-12 text-center">
                <div className="text-gray-400 mb-4">
                  <svg className="w-24 h-24 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <h2 className="text-2xl font-bold text-gray-600 mb-2">Waiting for auction to start...</h2>
                <p className="text-gray-500">The first player will be presented shortly</p>
              </div>
            )}

            {/* Bid History Panel */}
            <div className="bg-white rounded-lg shadow-2xl p-6">
              <h3 className="text-xl font-bold text-gray-800 mb-4">📜 Bid History</h3>
              <div className="max-h-64 overflow-y-auto space-y-2">
                {bidHistory.length === 0 ? (
                  <p className="text-gray-500 text-center py-4">No bids yet</p>
                ) : (
                  bidHistory.map((entry, index) => (
                    <div key={index} className="p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition">
                      {entry.type === 'new_player' && (
                        <p className="text-gray-700">
                          <span className="font-bold text-blue-600">New Player:</span> {entry.player}
                          <span className="text-xs text-gray-500 ml-2">{entry.timestamp}</span>
                        </p>
                      )}
                      {entry.type === 'bid' && (
                        <p className="text-gray-700">
                          <span className="font-bold text-green-600">{entry.username}</span> bid ₹{entry.amount}L
                          <span className="text-xs text-gray-500 ml-2">{entry.timestamp}</span>
                        </p>
                      )}
                      {entry.type === 'sold' && (
                        <p className="text-gray-700">
                          <span className="font-bold text-purple-600">SOLD!</span> {entry.player} to {entry.soldTo} for ₹{entry.price}L
                          <span className="text-xs text-gray-500 ml-2">{entry.timestamp}</span>
                        </p>
                      )}
                      {entry.type === 'completed' && (
                        <p className="text-gray-700 font-bold text-center">
                          🎉 {entry.message}
                          <span className="text-xs text-gray-500 ml-2">{entry.timestamp}</span>
                        </p>
                      )}
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>

          {/* Teams Sidebar - Right Side */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-2xl p-6 sticky top-4">
              <h3 className="text-xl font-bold text-gray-800 mb-4">👥 Teams</h3>
              <div className="space-y-3 max-h-[calc(100vh-200px)] overflow-y-auto">
                {teams.length === 0 ? (
                  <p className="text-gray-500 text-center py-4">No teams yet</p>
                ) : (
                  teams.map((team, index) => (
                    <div
                      key={index}
                      className={`p-4 rounded-lg border-2 transition ${
                        team.username === username
                          ? 'bg-blue-50 border-blue-500'
                          : 'bg-gray-50 border-gray-200'
                      }`}
                    >
                      <div className="flex items-center mb-2">
                        {team.logo_url ? (
                          <img
                            src={team.logo_url}
                            alt={team.team_name}
                            className="w-10 h-10 rounded-full object-cover mr-2"
                          />
                        ) : (
                          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white font-bold mr-2">
                            {team.team_name?.charAt(0).toUpperCase() || 'T'}
                          </div>
                        )}
                        <div className="flex-1">
                          <p className="font-bold text-gray-800 text-sm truncate">
                            {team.team_name || team.username}
                          </p>
                          {team.username === username && (
                            <span className="text-xs text-blue-600 font-semibold">Your Team</span>
                          )}
                        </div>
                      </div>
                      <div className="space-y-1 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-600">Purse:</span>
                          <span className="font-bold text-green-600">₹{team.purse_left || team.initial_purse || 0}L</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Squad:</span>
                          <span className="font-bold text-blue-600">{team.squad_size || 0} players</span>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AuctionRoom
