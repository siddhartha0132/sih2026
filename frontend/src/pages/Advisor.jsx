import { useState } from 'react'
import { Link } from 'react-router-dom'
import InputForm from '../components/InputForm.jsx'
import ReportView from '../components/ReportView.jsx'
import { getAdvisory } from '../api/client.js'
import { useAuth } from '../context/AuthContext.jsx'

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
  const isPersonal = mode === 'personal'

  const [form, setForm] = useState(initialForm)
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
      setError(err.message || 'Something went wrong. Please check the backend is running.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container section">
      <h1>{isPersonal ? 'Build your business plan' : 'Try it now — no account needed'}</h1>
      <p>
        Enter your location, available capital, and business idea. We'll calculate your
        exact loan eligibility, match your scheme, and generate a local feasibility report.
        {isPersonal
          ? ' This run will be saved to your personal history automatically.'
          : ' Nothing is saved — this is a one-off, open-use report.'}
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
              ✅ Saved to your history.{' '}
              <Link to="/history">View all your saved plans</Link>
            </p>
          )}
          <ReportView
            response={result}
            fileLabel={`GramVyapaar_Report_${form.district}_${form.business_category}`}
          />
        </div>
      )}
    </div>
  )
}
