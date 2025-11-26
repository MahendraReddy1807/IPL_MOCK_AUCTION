import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { auctionAPI } from '../services/api'

function Results() {
  const { roomCode } = useParams()
  const navigate = useNavigate()
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchResults = async () => {
      try {
        setLoading(true)
        const response = await auctionAPI.getResults(roomCode)
        setResults(response.data)
        setError(null)
      } catch (err) {
        console.error('Error fetching results:', err)
        setError(err.response?.data?.message || 'Failed to load results')
      } finally {
        setLoading(false)
      }
    }

    if (roomCode) {
      fetchResults()
    }
  }, [roomCode])

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 flex items-center justify-center">
        <div className="text-white text-2xl">Loading results...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 flex items-center justify-center">
        <div className="bg-red-500 text-white px-6 py-4 rounded-lg">
          <p className="text-xl font-bold mb-2">Error</p>
          <p>{error}</p>
          <button
            onClick={() => navigate('/')}
            className="mt-4 bg-white text-red-500 px-4 py-2 rounded hover:bg-gray-100"
          >
            Back to Home
          </button>
        </div>
      </div>
    )
  }

  if (!results || !results.teams || results.teams.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 flex items-center justify-center">
        <div className="text-white text-xl">No results available</div>
      </div>
    )
  }

  const { teams, winner } = results

  // Sort teams by rating (highest first)
  const sortedTeams = [...teams].sort((a, b) => {
    const ratingA = a.rating?.overall_rating || 0
    const ratingB = b.rating?.overall_rating || 0
    return ratingB - ratingA
  })

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 py-8 px-4">
      <div className="container mx-auto max-w-7xl">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            🏆 Auction Results
          </h1>
          <p className="text-xl text-gray-300">Room Code: {roomCode}</p>
        </div>

        {/* Winner Announcement */}
        {winner && (
          <div className="bg-gradient-to-r from-yellow-400 to-yellow-600 rounded-lg p-6 mb-8 text-center shadow-2xl">
            <h2 className="text-3xl font-bold text-gray-900 mb-2">
              🎉 Winner: {winner.team_name} 🎉
            </h2>
            <p className="text-lg text-gray-800">Congratulations to {winner.username}!</p>
          </div>
        )}

        {/* Team Ratings Comparison */}
        <div className="bg-white/10 backdrop-blur-md rounded-lg p-6 mb-8">
          <h3 className="text-2xl font-bold text-white mb-4">Team Ratings Comparison</h3>
          <div className="space-y-4">
            {sortedTeams.map((team, index) => (
              <div key={team.team_id} className="bg-white/5 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-3">
                    <span className="text-2xl font-bold text-white">#{index + 1}</span>
                    {team.logo_url && (
                      <img
                        src={team.logo_url}
                        alt={team.team_name}
                        className="w-10 h-10 rounded-full object-cover"
                        onError={(e) => {
                          e.target.style.display = 'none'
                        }}
                      />
                    )}
                    <span className="text-xl font-semibold text-white">{team.team_name}</span>
                  </div>
                  <span className="text-2xl font-bold text-yellow-400">
                    {team.rating?.overall_rating?.toFixed(1) || 'N/A'}
                  </span>
                </div>
                {/* Rating Bar */}
                <div className="w-full bg-gray-700 rounded-full h-4 overflow-hidden">
                  <div
                    className="bg-gradient-to-r from-green-400 to-blue-500 h-full rounded-full transition-all duration-500"
                    style={{ width: `${team.rating?.overall_rating || 0}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Detailed Team Cards */}
        <div className="space-y-8">
          {sortedTeams.map((team) => (
            <TeamCard key={team.team_id} team={team} />
          ))}
        </div>

        {/* Back Button */}
        <div className="text-center mt-8">
          <button
            onClick={() => navigate('/')}
            className="bg-white text-purple-900 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
          >
            Back to Home
          </button>
        </div>
      </div>
    </div>
  )
}

function TeamCard({ team }) {
  const [activeTab, setActiveTab] = useState('squad')

  return (
    <div className="bg-white/10 backdrop-blur-md rounded-lg overflow-hidden shadow-xl">
      {/* Team Header */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 p-6">
        <div className="flex items-center gap-4 mb-4">
          {team.logo_url && (
            <img
              src={team.logo_url}
              alt={team.team_name}
              className="w-16 h-16 rounded-full object-cover border-4 border-white"
              onError={(e) => {
                e.target.style.display = 'none'
              }}
            />
          )}
          <div>
            <h3 className="text-3xl font-bold text-white">{team.team_name}</h3>
            <p className="text-gray-200">Owner: {team.username}</p>
          </div>
        </div>
        <div className="flex gap-4 text-white">
          <div className="bg-white/20 rounded px-4 py-2">
            <span className="text-sm">Purse Left</span>
            <p className="text-xl font-bold">₹{team.purse_left?.toFixed(1)}L</p>
          </div>
          <div className="bg-white/20 rounded px-4 py-2">
            <span className="text-sm">Squad Size</span>
            <p className="text-xl font-bold">{team.squad?.length || 0}</p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-white/20">
        <button
          onClick={() => setActiveTab('squad')}
          className={`flex-1 py-3 px-4 font-semibold transition-colors ${
            activeTab === 'squad'
              ? 'bg-white/20 text-white border-b-2 border-white'
              : 'text-gray-300 hover:bg-white/10'
          }`}
        >
          Full Squad ({team.squad?.length || 0})
        </button>
        <button
          onClick={() => setActiveTab('playingXI')}
          className={`flex-1 py-3 px-4 font-semibold transition-colors ${
            activeTab === 'playingXI'
              ? 'bg-white/20 text-white border-b-2 border-white'
              : 'text-gray-300 hover:bg-white/10'
          }`}
        >
          Playing XI ({team.playing_xi?.length || 0})
        </button>
        <button
          onClick={() => setActiveTab('ratings')}
          className={`flex-1 py-3 px-4 font-semibold transition-colors ${
            activeTab === 'ratings'
              ? 'bg-white/20 text-white border-b-2 border-white'
              : 'text-gray-300 hover:bg-white/10'
          }`}
        >
          Ratings
        </button>
      </div>

      {/* Tab Content */}
      <div className="p-6">
        {activeTab === 'squad' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {team.squad?.map((player) => (
              <PlayerCard
                key={player.id}
                player={player}
                isPlayingXI={team.playing_xi?.some((p) => p.id === player.id)}
                isImpact={team.impact_player?.id === player.id}
              />
            ))}
          </div>
        )}

        {activeTab === 'playingXI' && (
          <div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
              {team.playing_xi?.map((player) => (
                <PlayerCard key={player.id} player={player} isPlayingXI={true} />
              ))}
            </div>
            {team.impact_player && (
              <div className="mt-6 border-t border-white/20 pt-6">
                <h4 className="text-xl font-bold text-white mb-4">⚡ Impact Player</h4>
                <div className="max-w-md">
                  <PlayerCard player={team.impact_player} isImpact={true} />
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'ratings' && team.rating && (
          <div className="space-y-4">
            <RatingBar
              label="Overall Rating"
              value={team.rating.overall_rating}
              color="from-yellow-400 to-orange-500"
            />
            <RatingBar
              label="Batting Strength"
              value={team.rating.batting_rating}
              color="from-green-400 to-emerald-500"
            />
            <RatingBar
              label="Bowling Strength"
              value={team.rating.bowling_rating}
              color="from-blue-400 to-cyan-500"
            />
            <RatingBar
              label="Team Balance"
              value={team.rating.balance_score}
              color="from-purple-400 to-pink-500"
            />
            <RatingBar
              label="Bench Depth"
              value={team.rating.bench_depth}
              color="from-indigo-400 to-blue-500"
            />
            <RatingBar
              label="Role Coverage"
              value={team.rating.role_coverage}
              color="from-red-400 to-orange-500"
            />
          </div>
        )}
      </div>
    </div>
  )
}

function PlayerCard({ player, isPlayingXI, isImpact }) {
  const roleColors = {
    BAT: 'bg-green-500',
    BOWL: 'bg-blue-500',
    AR: 'bg-purple-500',
    WK: 'bg-yellow-500',
  }

  const roleColor = roleColors[player.role] || 'bg-gray-500'

  return (
    <div
      className={`bg-white/5 rounded-lg p-4 border-2 transition-all hover:bg-white/10 ${
        isPlayingXI ? 'border-green-400' : 'border-transparent'
      } ${isImpact ? 'border-yellow-400 shadow-lg shadow-yellow-400/50' : ''}`}
    >
      <div className="flex items-start justify-between mb-2">
        <div className="flex-1">
          <h4 className="text-white font-semibold text-lg">{player.name}</h4>
          <p className="text-gray-400 text-sm">{player.country}</p>
        </div>
        <span className={`${roleColor} text-white text-xs px-2 py-1 rounded font-bold`}>
          {player.role}
        </span>
      </div>
      <div className="flex justify-between items-center mt-3">
        <div className="text-sm">
          <span className="text-gray-400">Rating:</span>
          <span className="text-white font-bold ml-1">{player.overall_score?.toFixed(1)}</span>
        </div>
        <div className="text-sm">
          <span className="text-gray-400">Price:</span>
          <span className="text-white font-bold ml-1">₹{player.price?.toFixed(1)}L</span>
        </div>
      </div>
      {isPlayingXI && (
        <div className="mt-2 text-xs text-green-400 font-semibold">✓ Playing XI</div>
      )}
      {isImpact && (
        <div className="mt-2 text-xs text-yellow-400 font-semibold">⚡ Impact Player</div>
      )}
    </div>
  )
}

function RatingBar({ label, value, color }) {
  return (
    <div>
      <div className="flex justify-between mb-2">
        <span className="text-white font-semibold">{label}</span>
        <span className="text-white font-bold">{value?.toFixed(1) || 'N/A'}</span>
      </div>
      <div className="w-full bg-gray-700 rounded-full h-6 overflow-hidden">
        <div
          className={`bg-gradient-to-r ${color} h-full rounded-full transition-all duration-500 flex items-center justify-end pr-2`}
          style={{ width: `${value || 0}%` }}
        >
          <span className="text-white text-xs font-bold">{value?.toFixed(0)}%</span>
        </div>
      </div>
    </div>
  )
}

export default Results
