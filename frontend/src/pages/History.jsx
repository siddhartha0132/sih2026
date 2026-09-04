import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'
import { getHistoryList } from '../api/client.js'
import { useLanguage } from '../LanguageContext.jsx'
import { t } from '../i18n.js'

export default function History() {
  const { token, user } = useAuth()
  const { language } = useLanguage()
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
    const key = e.business_name || t(language, 'history.untitledPlan')
    acc[key] = acc[key] || []
    acc[key].push(e)
    return acc
  }, {})

  return (
    <div className="container section">
      <h1 style={{ fontSize: '2rem' }}>{t(language, 'history.title')}</h1>
      <p>{t(language, 'history.signedInAs', { name: user?.name })}</p>

      {loading && <p>{t(language, 'history.loading')}</p>}
      {error && <div className="error-box">{error}</div>}

      {!loading && entries.length === 0 && (
        <div className="panel" style={{ marginTop: 24 }}>
          <p style={{ margin: 0 }}>{t(language, 'history.noPlansYet')}</p>
          <Link to="/advisor/personal" className="btn btn-primary" style={{ marginTop: 16 }}>
            {t(language, 'history.buildFirstPlan')}
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
                  {e.business_category} · {t(language, 'history.score', { score: e.business_opportunity_score })} ·{' '}
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
