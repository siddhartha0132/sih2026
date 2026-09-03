import { Routes, Route, Link, useNavigate } from 'react-router-dom'
import Landing from './pages/Landing.jsx'
import Advisor from './pages/Advisor.jsx'
import Login from './pages/Login.jsx'
import History from './pages/History.jsx'
import HistoryDetail from './pages/HistoryDetail.jsx'
import ProtectedRoute from './components/ProtectedRoute.jsx'
import { AuthProvider, useAuth } from './context/AuthContext.jsx'

function Header() {
  const { isLoggedIn, user, logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/')
  }

  return (
    <header className="site-header">
      <div className="site-header-inner">
        <Link to="/" className="brand">
          <span className="brand-mark" />
          GramVyapaar AI
        </Link>
        <div style={{ display: 'flex', alignItems: 'center', gap: 20 }}>
          <span className="tagline">Right Advice. Right Scheme. Stronger Future.</span>
          {isLoggedIn ? (
            <>
              <Link to="/history">My plans</Link>
              <span className="tagline">Hi, {user?.name?.split(' ')[0]}</span>
              <button className="btn btn-secondary" onClick={handleLogout}>Log out</button>
            </>
          ) : (
            <Link to="/login" className="btn btn-secondary">Log in</Link>
          )}
        </div>
      </div>
    </header>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <Header />
      <main>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={<Login />} />
          <Route path="/advisor/open" element={<Advisor mode="open" />} />
          <Route
            path="/advisor/personal"
            element={
              <ProtectedRoute>
                <Advisor mode="personal" />
              </ProtectedRoute>
            }
          />
          <Route
            path="/history"
            element={
              <ProtectedRoute>
                <History />
              </ProtectedRoute>
            }
          />
          <Route
            path="/history/:id"
            element={
              <ProtectedRoute>
                <HistoryDetail />
              </ProtectedRoute>
            }
          />
        </Routes>
      </main>
      <footer>
        Built for SIH26091 — Ministry of Social Justice &amp; Empowerment · Team Lumicore
      </footer>
    </AuthProvider>
  )
}
