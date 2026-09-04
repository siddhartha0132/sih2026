import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'
import { getHistoryEntry } from '../api/client.js'
import ReportView from '../components/ReportView.jsx'

export default function HistoryDetail() {
  const { id } = useParams()
  const { token } = useAuth()
  const [entry, setEntry] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    getHistoryEntry(token, id)
      .then(setEntry)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [token, id])

  return (
    <div className="container section">
      <Link to="/history">&larr; Back to my saved plans</Link>
      {loading && <p>Loading...</p>}
      {error && <div className="error-box" style={{ marginTop: 16 }}>{error}</div>}
      {entry && (
        <>
          <h1 style={{ fontSize: '2rem', marginTop: 16 }}>
            {entry.business_name || 'Untitled plan'}
          </h1>
          <p>
            Saved {new Date(entry.created_at).toLocaleString()} — {entry.request.village},{' '}
            {entry.request.district} · {entry.request.business_category}
          </p>
          <div style={{ marginTop: 24 }}>
            <ReportView
              response={entry.response}
              fileLabel={`GramVyapaar_${entry.request.district}_${entry.request.business_category}_${entry.id}`}
            />
          </div>
        </>
      )}
    </div>
  )
}
