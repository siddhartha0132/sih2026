const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api'

async function handleResponse(res) {
  if (!res.ok) {
    const text = await res.text()
    let detail = text
    try {
      detail = JSON.parse(text).detail || text
    } catch {
      // not JSON, keep raw text
    }
    throw new Error(detail || `Request failed (${res.status})`)
  }
  return res.json()
}

/**
 * getAdvisory: pass `token` only for personal-use (logged-in) requests. When
 * token is omitted/null this is a stateless open-use request — the backend
 * never writes anything to history in that case.
 */
export async function getAdvisory(payload, token) {
  const headers = { 'Content-Type': 'application/json' }
  if (token) headers['Authorization'] = `Bearer ${token}`
  const res = await fetch(`${API_BASE}/advisory`, {
    method: 'POST',
    headers,
    body: JSON.stringify(payload),
  })
  return handleResponse(res)
}

export async function signupRequest({ name, phone_or_email, password }) {
  const res = await fetch(`${API_BASE}/auth/signup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, phone_or_email, password }),
  })
  return handleResponse(res)
}

export async function loginRequest({ phone_or_email, password }) {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ phone_or_email, password }),
  })
  return handleResponse(res)
}

export async function getHistoryList(token, businessName) {
  const url = new URL(`${API_BASE}/history`)
  if (businessName) url.searchParams.set('business_name', businessName)
  const res = await fetch(url, {
    headers: { Authorization: `Bearer ${token}` },
  })
  return handleResponse(res)
}

export async function getHistoryEntry(token, id) {
  const res = await fetch(`${API_BASE}/history/${id}`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  return handleResponse(res)
}
