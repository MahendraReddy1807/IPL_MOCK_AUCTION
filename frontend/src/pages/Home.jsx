import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { roomAPI } from '../services/api'

function Home() {
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [roomCode, setRoomCode] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleCreateRoom = async () => {
    if (!username.trim()) {
      setError('Please enter a username')
      return
    }

    setLoading(true)
    setError('')

    try {
      const response = await roomAPI.createRoom(username.trim())
      const { room_code } = response.data
      
      localStorage.setItem('username', username.trim())
      localStorage.setItem('roomCode', room_code)
      
      navigate(`/lobby/${room_code}`)
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to create room')
    } finally {
      setLoading(false)
    }
  }

  const handleJoinRoom = async () => {
    if (!username.trim()) {
      setError('Please enter a username')
      return
    }

    if (!roomCode.trim()) {
      setError('Please enter a room code')
      return
    }

    setLoading(true)
    setError('')

    try {
      await roomAPI.joinRoom(roomCode.trim(), username.trim())
      
      localStorage.setItem('username', username.trim())
      localStorage.setItem('roomCode', roomCode.trim())
      
      navigate(`/lobby/${roomCode.trim()}`)
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to join room')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 flex items-center justify-center px-4 py-8">
      <div className="max-w-5xl w-full">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <div className="mb-6 animate-bounce">
            <span className="text-8xl">🏏</span>
          </div>
          <h1 className="text-6xl font-bold text-white mb-4 tracking-tight animate-fade-in">
            IPL Auction Arena
          </h1>
          <p className="text-blue-200 text-xl mb-6">
            Build your dream cricket team with 500+ players!
          </p>
          <div className="flex justify-center gap-6 text-white/80 text-sm flex-wrap">
            <div className="flex items-center gap-2">
              <span className="text-green-400">✓</span>
              <span>Real-time Bidding</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-green-400">✓</span>
              <span>AI Team Analysis</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-green-400">✓</span>
              <span>2-10 Players</span>
            </div>
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          {/* Create Room Card */}
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl shadow-2xl p-8 border border-white/20 hover:border-white/40 transition-all duration-300 hover:scale-105 hover:shadow-blue-500/50">
            <div className="text-center mb-6">
              <div className="w-16 h-16 bg-blue-500 rounded-full flex items-center justify-center mx-auto mb-4 shadow-lg">
                <span className="text-3xl">🎯</span>
              </div>
              <h2 className="text-2xl font-bold text-white mb-2">Create New Room</h2>
              <p className="text-blue-200 text-sm">Start a new auction and invite friends</p>
            </div>

            {error && !roomCode && (
              <div className="mb-4 p-3 bg-red-500/20 border border-red-500/50 text-red-200 rounded-lg text-sm animate-shake">
                ⚠️ {error}
              </div>
            )}

            <div className="space-y-4">
              <div>
                <label htmlFor="create-username" className="block text-sm font-medium text-white/90 mb-2">
                  Your Username
                </label>
                <input
                  id="create-username"
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="Enter your username"
                  className="w-full px-4 py-3 bg-white/10 border border-white/30 rounded-lg focus:ring-2 focus:ring-blue-400 focus:border-transparent outline-none transition text-white placeholder-white/50"
                  disabled={loading}
                  onKeyDown={(e) => e.key === 'Enter' && handleCreateRoom()}
                />
              </div>

              <button
                onClick={handleCreateRoom}
                disabled={loading}
                className="w-full bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white font-semibold py-4 px-6 rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 active:scale-95"
              >
                {loading ? (
                  <span className="flex items-center justify-center gap-2">
                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                    </svg>
                    Creating...
                  </span>
                ) : (
                  '🎯 Create Room'
                )}
              </button>
            </div>
          </div>

          {/* Join Room Card */}
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl shadow-2xl p-8 border border-white/20 hover:border-white/40 transition-all duration-300 hover:scale-105 hover:shadow-green-500/50">
            <div className="text-center mb-6">
              <div className="w-16 h-16 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-4 shadow-lg">
                <span className="text-3xl">🚪</span>
              </div>
              <h2 className="text-2xl font-bold text-white mb-2">Join Existing Room</h2>
              <p className="text-blue-200 text-sm">Enter a room code to join an auction</p>
            </div>

            {error && roomCode && (
              <div className="mb-4 p-3 bg-red-500/20 border border-red-500/50 text-red-200 rounded-lg text-sm animate-shake">
                ⚠️ {error}
              </div>
            )}

            <div className="space-y-4">
              <div>
                <label htmlFor="join-username" className="block text-sm font-medium text-white/90 mb-2">
                  Your Username
                </label>
                <input
                  id="join-username"
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="Enter your username"
                  className="w-full px-4 py-3 bg-white/10 border border-white/30 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent outline-none transition text-white placeholder-white/50"
                  disabled={loading}
                />
              </div>

              <div>
                <label htmlFor="roomCode" className="block text-sm font-medium text-white/90 mb-2">
                  Room Code
                </label>
                <input
                  id="roomCode"
                  type="text"
                  value={roomCode}
                  onChange={(e) => setRoomCode(e.target.value.toUpperCase())}
                  placeholder="Enter room code"
                  className="w-full px-4 py-3 bg-white/10 border border-white/30 rounded-lg focus:ring-2 focus:ring-green-400 focus:border-transparent outline-none transition uppercase text-white placeholder-white/50 tracking-wider text-center text-xl font-bold"
                  disabled={loading}
                  maxLength={10}
                  onKeyDown={(e) => e.key === 'Enter' && handleJoinRoom()}
                />
              </div>

              <button
                onClick={handleJoinRoom}
                disabled={loading}
                className="w-full bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white font-semibold py-4 px-6 rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 active:scale-95"
              >
                {loading ? (
                  <span className="flex items-center justify-center gap-2">
                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                    </svg>
                    Joining...
                  </span>
                ) : (
                  '🚪 Join Room'
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Features Section */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
          <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10 hover:bg-white/10 transition-all duration-300">
            <div className="text-4xl mb-3">⚡</div>
            <h3 className="text-white font-semibold mb-2">Real-Time Bidding</h3>
            <p className="text-blue-200 text-sm">Live auction with 30-second timer per player</p>
          </div>
          <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10 hover:bg-white/10 transition-all duration-300">
            <div className="text-4xl mb-3">🤖</div>
            <h3 className="text-white font-semibold mb-2">AI Analysis</h3>
            <p className="text-blue-200 text-sm">Automatic playing XI selection and team ratings</p>
          </div>
          <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10 hover:bg-white/10 transition-all duration-300">
            <div className="text-4xl mb-3">🏆</div>
            <h3 className="text-white font-semibold mb-2">500+ Players</h3>
            <p className="text-blue-200 text-sm">Comprehensive player pool with detailed stats</p>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-8 text-blue-200/60 text-sm">
          <p>Minimum 2 players • Maximum 10 players • Best experienced on desktop</p>
        </div>
      </div>
    </div>
  )
}

export default Home
