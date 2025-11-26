import { io } from 'socket.io-client'

const SOCKET_URL = import.meta.env.VITE_SOCKET_URL || 'http://localhost:5000'

class SocketService {
  constructor() {
    this.socket = null
    this.connectionCallbacks = []
    this.disconnectionCallbacks = []
    this.reconnectionCallbacks = []
  }

  /**
   * Connect to the Socket.IO server
   * @returns {Socket} The socket instance
   */
  connect() {
    if (!this.socket) {
      this.socket = io(SOCKET_URL, {
        transports: ['websocket', 'polling'],
        autoConnect: true,
        reconnection: true,
        reconnectionAttempts: 5,
        reconnectionDelay: 1000,
        reconnectionDelayMax: 5000,
        timeout: 20000
      })

      // Set up connection event handlers
      this.setupConnectionHandlers()
    }
    return this.socket
  }

  /**
   * Set up connection, disconnection, and reconnection handlers
   */
  setupConnectionHandlers() {
    if (!this.socket) return

    this.socket.on('connect', () => {
      console.log('Socket connected:', this.socket.id)
      this.connectionCallbacks.forEach(callback => callback())
    })

    this.socket.on('disconnect', (reason) => {
      console.log('Socket disconnected:', reason)
      this.disconnectionCallbacks.forEach(callback => callback(reason))
    })

    this.socket.on('reconnect', (attemptNumber) => {
      console.log('Socket reconnected after', attemptNumber, 'attempts')
      this.reconnectionCallbacks.forEach(callback => callback(attemptNumber))
    })

    this.socket.on('reconnect_attempt', (attemptNumber) => {
      console.log('Reconnection attempt:', attemptNumber)
    })

    this.socket.on('reconnect_error', (error) => {
      console.error('Reconnection error:', error)
    })

    this.socket.on('reconnect_failed', () => {
      console.error('Reconnection failed after all attempts')
    })

    this.socket.on('connect_error', (error) => {
      console.error('Connection error:', error)
    })
  }

  /**
   * Disconnect from the Socket.IO server
   */
  disconnect() {
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
    }
  }

  /**
   * Emit an event to the server
   * @param {string} event - Event name
   * @param {*} data - Data to send
   */
  emit(event, data) {
    if (this.socket && this.socket.connected) {
      this.socket.emit(event, data)
    } else {
      console.warn('Socket not connected. Cannot emit event:', event)
    }
  }

  /**
   * Register an event listener
   * @param {string} event - Event name
   * @param {Function} callback - Callback function
   */
  on(event, callback) {
    if (this.socket) {
      this.socket.on(event, callback)
    }
  }

  /**
   * Unregister an event listener
   * @param {string} event - Event name
   * @param {Function} callback - Callback function
   */
  off(event, callback) {
    if (this.socket) {
      if (callback) {
        this.socket.off(event, callback)
      } else {
        this.socket.off(event)
      }
    }
  }

  /**
   * Register a callback for connection events
   * @param {Function} callback - Callback function
   */
  onConnect(callback) {
    this.connectionCallbacks.push(callback)
  }

  /**
   * Register a callback for disconnection events
   * @param {Function} callback - Callback function
   */
  onDisconnect(callback) {
    this.disconnectionCallbacks.push(callback)
  }

  /**
   * Register a callback for reconnection events
   * @param {Function} callback - Callback function
   */
  onReconnect(callback) {
    this.reconnectionCallbacks.push(callback)
  }

  /**
   * Check if socket is connected
   * @returns {boolean} Connection status
   */
  isConnected() {
    return this.socket && this.socket.connected
  }

  /**
   * Get the socket ID
   * @returns {string|null} Socket ID or null if not connected
   */
  getSocketId() {
    return this.socket ? this.socket.id : null
  }

  /**
   * Join a room
   * @param {string} roomCode - Room code
   * @param {string} username - Username
   */
  joinRoom(roomCode, username) {
    this.emit('join_room', { room_code: roomCode, username })
  }

  /**
   * Place a bid
   * @param {string} roomCode - Room code
   * @param {string} username - Username
   */
  placeBid(roomCode, username) {
    this.emit('place_bid', { room_code: roomCode, username })
  }

  /**
   * Start auction
   * @param {string} roomCode - Room code
   */
  startAuction(roomCode) {
    this.emit('start_auction', { room_code: roomCode })
  }
}

export default new SocketService()
