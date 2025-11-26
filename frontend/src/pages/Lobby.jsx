import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { roomAPI, teamAPI } from '../services/api'
import socketService from '../services/socket'

function Lobby() {
  const { roomCode } = useParams()
  const navigate = useNavigate()
  
  // State management
  const [username, setUsername] = useState('')
  const [isHost, setIsHost] = useState(false)
  const [participants, setParticipants] = useState([])
  const [roomDetails, setRoomDetails] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  
  // Team configuration state
  const [teamName, setTeamName] = useState('')
  const [logoFile, setLogoFile] = useState(null)
  const [logoPreview, setLogoPreview] = useState('')
  const [purse, setPurse] = useState(100)
  const [teamConfigured, setTeamConfigured] = useState(false)
  const [configuring, setConfiguring] = useState(false)
  const [configError, setConfigError] = useState('')

  // Load username and room details on mount
  useEffect(() => {
    const storedUsername = localStorage.getItem('username')
    const storedRoomCode = localStorage.getItem('roomCode')
    
    if (!storedUsername || storedRoomCode !== roomCode) {
      navigate('/')
      return
    }
    
    setUsername(storedUsername)
    loadRoomDetails(storedUsername)
  }, [roomCode, navigate])

  // Set up Socket.IO connection
  useEffect(() => {
    if (!username) return

    const socket = socketService.connect()
    
    // Join the room
    socketService.emit('join_room', {
      room_code: roomCode,
      username: username
    })

    // Listen for user joined events
    const handleUserJoined = (data) => {
      console.log('User joined:', data)
      setParticipants(data.participants || [])
    }

    // Listen for user left events
    const handleUserLeft = (data) => {
      console.log('User left:', data)
      setParticipants(data.participants || [])
    }

    // Listen for auction started event
    const handleAuctionStarted = (data) => {
      console.log('Auction started:', data)
      navigate(`/auction/${roomCode}`)
    }

    socketService.on('user_joined', handleUserJoined)
    socketService.on('user_left', handleUserLeft)
    socketService.on('auction_started', handleAuctionStarted)

    // Cleanup on unmount
    return () => {
      socketService.off('user_joined', handleUserJoined)
      socketService.off('user_left', handleUserLeft)
      socketService.off('auction_started', handleAuctionStarted)
      socketService.emit('leave_room', {
        room_code: roomCode,
        username: username
      })
    }
  }, [username, roomCode, navigate])

  const loadRoomDetails = async (currentUsername) => {
    try {
      const response = await roomAPI.getRoom(roomCode)
      const data = response.data
      
      setRoomDetails(data)
      setParticipants(data.participants || [])
      setIsHost(data.host_username === currentUsername)
      setLoading(false)
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to load room details')
      setLoading(false)
    }
  }

  const handleLogoChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      setLogoFile(file)
      // Create preview
      const reader = new FileReader()
      reader.onloadend = () => {
        setLogoPreview(reader.result)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleConfigureTeam = async (e) => {
    e.preventDefault()
    
    if (!teamName.trim()) {
      setConfigError('Team name is required')
      return
    }

    if (purse <= 0) {
      setConfigError('Purse must be a positive number')
      return
    }

    setConfiguring(true)
    setConfigError('')

    try {
      let logoUrl = ''
      
      // Upload logo if provided
      if (logoFile) {
        const formData = new FormData()
        formData.append('logo', logoFile)
        
        const uploadResponse = await teamAPI.uploadLogo(formData)
        logoUrl = uploadResponse.data.logo_url
      }

      // Configure team
      await teamAPI.configureTeam({
        room_code: roomCode,
        username: username,
        team_name: teamName.trim(),
        logo_url: logoUrl,
        purse: purse
      })

      setTeamConfigured(true)
      setConfiguring(false)
    } catch (err) {
      setConfigError(err.response?.data?.message || 'Failed to configure team')
      setConfiguring(false)
    }
  }

  const handleStartAuction = () => {
    if (!isHost) return
    
    const minUsers = roomDetails?.min_users || 2
    if (participants.length < minUsers) {
      setError(`At least ${minUsers} participants required to start auction`)
      return
    }

    // Emit start auction event
    socketService.emit('start_auction', {
      room_code: roomCode,
      host_username: username
    })
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading lobby...</div>
      </div>
    )
  }

  if (error && !roomDetails) {
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
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 py-8 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Auction Lobby</h1>
          <div className="inline-block bg-white rounded-lg px-6 py-3 shadow-lg">
            <p className="text-sm text-gray-600 mb-1">Room Code</p>
            <p className="text-3xl font-bold text-blue-600 tracking-wider">{roomCode}</p>
          </div>
          {isHost && (
            <div className="mt-4">
              <span className="inline-block bg-yellow-400 text-yellow-900 px-4 py-2 rounded-full text-sm font-semibold">
                👑 You are the Host
              </span>
            </div>
          )}
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg max-w-2xl mx-auto">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Participants Panel */}
          <div className="bg-white rounded-lg shadow-2xl p-6">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">
              Participants ({participants.length}/{roomDetails?.max_users || 10})
            </h2>
            
            <div className="space-y-2 mb-6">
              {participants.length === 0 ? (
                <p className="text-gray-500 text-center py-4">No participants yet</p>
              ) : (
                participants.map((participant, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition"
                  >
                    <div className="flex items-center">
                      <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center text-white font-bold mr-3">
                        {participant.charAt(0).toUpperCase()}
                      </div>
                      <span className="font-medium text-gray-800">{participant}</span>
                    </div>
                    {participant === roomDetails?.host_username && (
                      <span className="text-yellow-600 text-sm font-semibold">👑 Host</span>
                    )}
                    {participant === username && (
                      <span className="text-blue-600 text-sm font-semibold">You</span>
                    )}
                  </div>
                ))
              )}
            </div>

            <div className="border-t pt-4">
              <p className="text-sm text-gray-600 mb-2">
                Minimum participants: {roomDetails?.min_users || 2}
              </p>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all duration-300 ${
                    participants.length >= (roomDetails?.min_users || 2)
                      ? 'bg-green-500'
                      : 'bg-blue-500'
                  }`}
                  style={{
                    width: `${Math.min(
                      (participants.length / (roomDetails?.min_users || 2)) * 100,
                      100
                    )}%`
                  }}
                ></div>
              </div>
            </div>
          </div>

          {/* Team Configuration Panel */}
          <div className="bg-white rounded-lg shadow-2xl p-6">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">Team Configuration</h2>
            
            {teamConfigured ? (
              <div className="text-center py-8">
                <div className="w-20 h-20 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <h3 className="text-xl font-bold text-gray-800 mb-2">Team Configured!</h3>
                <p className="text-gray-600 mb-4">Team: {teamName}</p>
                <p className="text-gray-600">Purse: ₹{purse} Lakhs</p>
                {logoPreview && (
                  <div className="mt-4">
                    <img src={logoPreview} alt="Team Logo" className="w-24 h-24 mx-auto rounded-lg object-cover" />
                  </div>
                )}
              </div>
            ) : (
              <form onSubmit={handleConfigureTeam} className="space-y-4">
                {/* Team Name */}
                <div>
                  <label htmlFor="teamName" className="block text-sm font-medium text-gray-700 mb-2">
                    Team Name *
                  </label>
                  <input
                    id="teamName"
                    type="text"
                    value={teamName}
                    onChange={(e) => setTeamName(e.target.value)}
                    placeholder="Enter your team name"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                    disabled={configuring}
                    required
                  />
                </div>

                {/* Logo Upload */}
                <div>
                  <label htmlFor="logo" className="block text-sm font-medium text-gray-700 mb-2">
                    Team Logo (Optional)
                  </label>
                  <input
                    id="logo"
                    type="file"
                    accept="image/png,image/jpeg,image/jpg,image/gif"
                    onChange={handleLogoChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                    disabled={configuring}
                  />
                  {logoPreview && (
                    <div className="mt-2">
                      <img src={logoPreview} alt="Preview" className="w-20 h-20 rounded-lg object-cover" />
                    </div>
                  )}
                </div>

                {/* Purse */}
                <div>
                  <label htmlFor="purse" className="block text-sm font-medium text-gray-700 mb-2">
                    Starting Purse (Lakhs) *
                  </label>
                  <input
                    id="purse"
                    type="number"
                    value={purse}
                    onChange={(e) => setPurse(Number(e.target.value))}
                    min="1"
                    step="1"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                    disabled={configuring}
                    required
                  />
                </div>

                {/* Config Error */}
                {configError && (
                  <div className="p-3 bg-red-100 border border-red-400 text-red-700 rounded-lg text-sm">
                    {configError}
                  </div>
                )}

                {/* Submit Button */}
                <button
                  type="submit"
                  disabled={configuring}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-4 rounded-lg transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {configuring ? 'Configuring...' : 'Configure Team'}
                </button>
              </form>
            )}
          </div>
        </div>

        {/* Start Auction Button (Host Only) */}
        {isHost && (
          <div className="mt-8 max-w-2xl mx-auto">
            <button
              onClick={handleStartAuction}
              disabled={participants.length < (roomDetails?.min_users || 2)}
              className="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-4 px-6 rounded-lg text-xl transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
            >
              {participants.length < (roomDetails?.min_users || 2)
                ? `Waiting for ${(roomDetails?.min_users || 2) - participants.length} more participant(s)...`
                : '🚀 Start Auction'}
            </button>
            {participants.length >= (roomDetails?.min_users || 2) && (
              <p className="text-center text-white mt-2 text-sm">
                All participants should configure their teams before starting
              </p>
            )}
          </div>
        )}

        {/* Waiting Message (Non-Host) */}
        {!isHost && (
          <div className="mt-8 max-w-2xl mx-auto text-center">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <p className="text-gray-700 text-lg">
                Waiting for the host to start the auction...
              </p>
              <div className="mt-4 flex justify-center space-x-2">
                <div className="w-3 h-3 bg-blue-500 rounded-full animate-bounce"></div>
                <div className="w-3 h-3 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-3 h-3 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default Lobby
