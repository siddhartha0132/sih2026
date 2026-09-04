import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'
import { getHistoryEntry } from '../api/client.js'
import ReportView from '../components/ReportView.jsx'
import { useLanguage } from '../LanguageContext.jsx'
import { t } from '../i18n.js'

export default function HistoryDetail() {
  const { id } = useParams()
  const { token } = useAuth()
  const { language: globalLanguage } = useLanguage()
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

  // Prefer the language the report was actually generated in (saved on the
  // request), falling back to the app's current global language if it's
  // somehow missing on older entries.
  const language = entry?.request?.language || globalLanguage

  return (
    <div className="container section">
      <Link to="/history">{t(language, 'historyDetail.back')}</Link>
      {loading && <p>{t(language, 'historyDetail.loading')}</p>}
      {error && <div className="error-box" style={{ marginTop: 16 }}>{error}</div>}
      {entry && (
        <>
          <h1 style={{ fontSize: '2rem', marginTop: 16 }}>
            {entry.business_name || t(language, 'historyDetail.untitledPlan')}
          </h1>
          <p>
            {t(language, 'historyDetail.saved', { date: new Date(entry.created_at).toLocaleString() })} — {entry.request.village},{' '}
            {entry.request.district} · {entry.request.business_category}
          </p>
          <div style={{ marginTop: 24 }}>
            <ReportView
              response={entry.response}
              language={language}
              fileLabel={`GramVyapaar_${entry.request.district}_${entry.request.business_category}_${entry.id}`}
            />
          </div>
        </>
      )}
    </div>
  )
}
