import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'
import { getHistoryList } from '../api/client.js'

export default function History() {
  const { token, user } = useAuth()
  const [entries, setEntries] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    getHistoryList(token)
      .then(setEntries)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [token])

  // Group by business_name so the same venture's check-ins (e.g. "1 hour in",
  // "3 hours later") read as one timeline rather than a flat list.
  const grouped = entries.reduce((acc, e) => {
    const key = e.business_name || 'Untitled plan'
    acc[key] = acc[key] || []
    acc[key].push(e)
    return acc
  }, {})

  return (
    <div className="container section">
      <h1 style={{ fontSize: '2rem' }}>My saved plans</h1>
      <p>Signed in as {user?.name}. Every report you generate here is saved automatically.</p>

      {loading && <p>Loading...</p>}
      {error && <div className="error-box">{error}</div>}

      {!loading && entries.length === 0 && (
        <div className="panel" style={{ marginTop: 24 }}>
          <p style={{ margin: 0 }}>No saved plans yet.</p>
          <Link to="/advisor/personal" className="btn btn-primary" style={{ marginTop: 16 }}>
            Build your first plan
          </Link>
        </div>
      )}

      {Object.entries(grouped).map(([businessName, group]) => (
        <div key={businessName} className="panel" style={{ marginTop: 24 }}>
          <h3>{businessName}</h3>
          <ul className="list-clean">
            {group.map((e) => (
              <li key={e.id}>
                <Link to={`/history/${e.id}`}>
                  {new Date(e.created_at).toLocaleString()} — {e.village}, {e.district} ·{' '}
                  {e.business_category} · Score {e.business_opportunity_score}/100 ·{' '}
                  {e.selected_scheme}
                </Link>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  )
}
