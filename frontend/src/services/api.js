import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

export const roomAPI = {
  createRoom: (hostUsername) => api.post('/rooms/create', { host_username: hostUsername }),
  joinRoom: (roomCode, username) => api.post('/rooms/join', { room_code: roomCode, username }),
  getRoom: (roomCode) => api.get(`/rooms/${roomCode}`)
}

export const teamAPI = {
  configureTeam: (data) => api.post('/teams/configure', data),
  uploadLogo: (formData) => api.post('/teams/upload-logo', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export const playerAPI = {
  getPlayers: () => api.get('/players')
}

export const auctionAPI = {
  getAuctionState: (roomCode) => api.get(`/auction/${roomCode}/state`),
  getResults: (roomCode) => api.get(`/results/${roomCode}`)
}

export default api
