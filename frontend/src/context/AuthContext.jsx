import { createContext, useContext, useEffect, useState } from 'react'
import { loginRequest, signupRequest } from '../api/client.js'

const AuthContext = createContext(null)

const TOKEN_KEY = 'gramvyapaar_token'
const USER_KEY = 'gramvyapaar_user'

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY))
  const [user, setUser] = useState(() => {
    const raw = localStorage.getItem(USER_KEY)
    return raw ? JSON.parse(raw) : null
  })

  useEffect(() => {
    if (token) localStorage.setItem(TOKEN_KEY, token)
    else localStorage.removeItem(TOKEN_KEY)
  }, [token])

  useEffect(() => {
    if (user) localStorage.setItem(USER_KEY, JSON.stringify(user))
    else localStorage.removeItem(USER_KEY)
  }, [user])

  function _applyAuthResponse(data) {
    setToken(data.access_token)
    setUser(data.user)
  }

  async function login(phone_or_email, password) {
    const data = await loginRequest({ phone_or_email, password })
    _applyAuthResponse(data)
    return data.user
  }

  async function signup(name, phone_or_email, password) {
    const data = await signupRequest({ name, phone_or_email, password })
    _applyAuthResponse(data)
    return data.user
  }

  function logout() {
    setToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ token, user, isLoggedIn: !!token, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within an AuthProvider')
  return ctx
}
