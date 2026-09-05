import { Routes, Route, Link, useNavigate } from 'react-router-dom'
import Landing from './pages/Landing.jsx'
import Advisor from './pages/Advisor.jsx'
import Login from './pages/Login.jsx'
import History from './pages/History.jsx'
import HistoryDetail from './pages/HistoryDetail.jsx'
import ProtectedRoute from './components/ProtectedRoute.jsx'
import { AuthProvider, useAuth } from './context/AuthContext.jsx'
import { LanguageProvider, useLanguage } from './LanguageContext.jsx'
import { LANGUAGES, t } from './i18n.js'

function LanguageSwitcher() {
  const { language, setLanguage } = useLanguage()
  return (
    <select
      aria-label="Language"
      value={language}
      onChange={(e) => setLanguage(e.target.value)}
      className="lang-switcher"
    >
      {LANGUAGES.map((l) => <option key={l.code} value={l.code}>{l.label}</option>)}
    </select>
  )
}

function Header() {
  const { isLoggedIn, user, logout } = useAuth()
  const { language } = useLanguage()
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
          <span>GramVyapaar AI</span>
        </Link>
        <div className="site-header-nav">
          <span className="tagline">{t(language, 'app.tagline')}</span>
          <LanguageSwitcher />
          {isLoggedIn ? (
            <>
              <Link to="/history">{t(language, 'app.myPlans')}</Link>
              <span className="tagline">{t(language, 'app.hi', { name: user?.name?.split(' ')[0] })}</span>
              <button className="btn btn-secondary" onClick={handleLogout}>{t(language, 'app.logOut')}</button>
            </>
          ) : (
            <Link to="/login" className="btn btn-secondary">{t(language, 'app.logIn')}</Link>
          )}
        </div>
      </div>
    </header>
  )
}

function Footer() {
  const { language } = useLanguage()
  return (
    <footer>
      {t(language, 'app.footer')}
    </footer>
  )
}

export default function App() {
  return (
    <LanguageProvider>
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
        <Footer />
      </AuthProvider>
    </LanguageProvider>
  )
}
