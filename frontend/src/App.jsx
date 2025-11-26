import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import Lobby from './pages/Lobby'
import AuctionRoom from './pages/AuctionRoom'
import Results from './pages/Results'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-100">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/lobby/:roomCode" element={<Lobby />} />
          <Route path="/auction/:roomCode" element={<AuctionRoom />} />
          <Route path="/results/:roomCode" element={<Results />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App
