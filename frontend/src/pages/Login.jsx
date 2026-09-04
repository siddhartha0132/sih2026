import { useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'
import { useLanguage } from '../LanguageContext.jsx'
import { t } from '../i18n.js'

export default function Login() {
  const { login, signup } = useAuth()
  const { language } = useLanguage()
  const navigate = useNavigate()
  const location = useLocation()
  const redirectTo = location.state?.from?.pathname || '/advisor/personal'

  const [mode, setMode] = useState('login') // 'login' | 'signup'
  const [name, setName] = useState('')
  const [phoneOrEmail, setPhoneOrEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      if (mode === 'login') {
        await login(phoneOrEmail, password)
      } else {
        await signup(name, phoneOrEmail, password)
      }
      navigate(redirectTo, { replace: true })
    } catch (err) {
      setError(err.message || t(language, 'login.errorFallback'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container section" style={{ maxWidth: 440 }}>
      <h1 style={{ fontSize: '2rem' }}>{mode === 'login' ? t(language, 'login.heading') : t(language, 'login.signupHeading')}</h1>
      <p>
        {t(language, 'login.description')}
      </p>

      <form onSubmit={handleSubmit} className="panel" style={{ marginTop: 24 }}>
        {mode === 'signup' && (
          <div className="field">
            <label htmlFor="name">{t(language, 'login.yourName')}</label>
            <input id="name" value={name} onChange={(e) => setName(e.target.value)} required />
          </div>
        )}
        <div className="field">
          <label htmlFor="poe">{t(language, 'login.phoneOrEmail')}</label>
          <input
            id="poe"
            value={phoneOrEmail}
            onChange={(e) => setPhoneOrEmail(e.target.value)}
            required
          />
        </div>
        <div className="field">
          <label htmlFor="password">{t(language, 'login.password')}</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            minLength={6}
            required
          />
        </div>

        {error && <div className="error-box">{error}</div>}

        <button className="btn btn-primary" type="submit" disabled={loading} style={{ width: '100%' }}>
          {loading ? t(language, 'login.pleaseWait') : mode === 'login' ? t(language, 'login.logIn') : t(language, 'login.signUp')}
        </button>
      </form>

      <p style={{ marginTop: 16 }}>
        {mode === 'login' ? (
          <>
            {t(language, 'login.newHere')}{' '}
            <a href="#" onClick={(e) => { e.preventDefault(); setMode('signup'); setError(null) }}>
              {t(language, 'login.createAccount')}
            </a>
          </>
        ) : (
          <>
            {t(language, 'login.alreadyHaveAccount')}{' '}
            <a href="#" onClick={(e) => { e.preventDefault(); setMode('login'); setError(null) }}>
              {t(language, 'login.logIn')}
            </a>
          </>
        )}
      </p>
    </div>
  )
}
