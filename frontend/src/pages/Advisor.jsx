import { useState } from 'react'
import { Link } from 'react-router-dom'
import InputForm from '../components/InputForm.jsx'
import ReportView from '../components/ReportView.jsx'
import { getAdvisory } from '../api/client.js'
import { useAuth } from '../context/AuthContext.jsx'
import { useLanguage } from '../LanguageContext.jsx'
import { t } from '../i18n.js'

const initialForm = {
  business_name: '',
  village: '',
  block: '',
  district: '',
  state: '',
  pincode: '',
  available_margin_capital: '',
  business_category: 'Dairy',
  business_category_other: '',
  applicant_gender: '',
  applicant_age: '',
  is_first_time_entrepreneur: true,
  language: 'en',
  business_stage: 'idea',
  legal_structure: 'none_informal',
  current_monthly_revenue: '',
  business_idea_description: '',
}

/**
 * One form + report screen used by both modes:
 *  - mode="open":     no token sent, nothing saved (route: /advisor/open)
 *  - mode="personal": token sent, backend auto-saves to history (route:
 *    /advisor/personal, wrapped in ProtectedRoute so you can't get here
 *    without being logged in)
 */
export default function Advisor({ mode }) {
  const { token } = useAuth()
  const { language: globalLanguage } = useLanguage()
  const isPersonal = mode === 'personal'

  const [form, setForm] = useState(() => ({ ...initialForm, language: globalLanguage }))
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function handleSubmit() {
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const payload = {
        ...form,
        available_margin_capital: Number(form.available_margin_capital),
        applicant_age: form.applicant_age ? Number(form.applicant_age) : null,
        business_name: isPersonal ? (form.business_name || null) : null,
        current_monthly_revenue: form.current_monthly_revenue ? Number(form.current_monthly_revenue) : null,
        business_idea_description: form.business_idea_description || null,
      }
      const data = await getAdvisory(payload, isPersonal ? token : null)
      setResult(data)
    } catch (err) {
      setError(err.message || t(form.language, 'advisor.errorFallback'))
    } finally {
      setLoading(false)
    }
  }

  const lang = form.language
  return (
    <div className="container section">
      <h1>{isPersonal ? t(lang, 'advisor.titlePersonal') : t(lang, 'advisor.titleOpen')}</h1>
      <p>
        {t(lang, 'advisor.description')}
        {isPersonal
          ? t(lang, 'advisor.savedNote')
          : t(lang, 'advisor.openNote')}
      </p>

      <div style={{ maxWidth: 640, marginTop: 24 }}>
        <InputForm
          form={form}
          setForm={setForm}
          onSubmit={handleSubmit}
          loading={loading}
          showBusinessName={isPersonal}
        />
      </div>

      {error && (
        <div className="error-box" style={{ marginTop: 24, maxWidth: 640 }}>
          {error}
        </div>
      )}

      {result && (
        <div style={{ marginTop: 40 }}>
          {isPersonal && result.history_id && (
            <p style={{ marginBottom: 16 }}>
              {t(lang, 'advisor.savedToHistory')}{' '}
              <Link to="/history">{t(lang, 'advisor.viewAllPlans')}</Link>
            </p>
          )}
          <ReportView
            response={result}
            language={lang}
            fileLabel={`GramVyapaar_Report_${form.district}_${form.business_category}`}
          />
        </div>
      )}
    </div>
  )
}
