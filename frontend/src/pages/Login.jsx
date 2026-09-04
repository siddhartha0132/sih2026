import { useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'

export default function Login() {
  const { login, signup } = useAuth()
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
      setError(err.message || 'Something went wrong.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container section" style={{ maxWidth: 440 }}>
      <h1 style={{ fontSize: '2rem' }}>{mode === 'login' ? 'Log in' : 'Create your account'}</h1>
      <p>
        Personal use saves every business plan you generate, so you can come
        back later and see how your numbers and advice change as your
        business grows.
      </p>

      <form onSubmit={handleSubmit} className="panel" style={{ marginTop: 24 }}>
        {mode === 'signup' && (
          <div className="field">
            <label htmlFor="name">Your name</label>
            <input id="name" value={name} onChange={(e) => setName(e.target.value)} required />
          </div>
        )}
        <div className="field">
          <label htmlFor="poe">Phone number or email</label>
          <input
            id="poe"
            value={phoneOrEmail}
            onChange={(e) => setPhoneOrEmail(e.target.value)}
            required
          />
        </div>
        <div className="field">
          <label htmlFor="password">Password</label>
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
          {loading ? 'Please wait...' : mode === 'login' ? 'Log in' : 'Sign up'}
        </button>
      </form>

      <p style={{ marginTop: 16 }}>
        {mode === 'login' ? (
          <>
            New here?{' '}
            <a href="#" onClick={(e) => { e.preventDefault(); setMode('signup'); setError(null) }}>
              Create an account
            </a>
          </>
        ) : (
          <>
            Already have an account?{' '}
            <a href="#" onClick={(e) => { e.preventDefault(); setMode('login'); setError(null) }}>
              Log in
            </a>
          </>
        )}
      </p>
    </div>
  )
}
