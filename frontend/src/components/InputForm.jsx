import { useState } from 'react'
import { getIdeaSuggestion } from '../api/client.js'

const CATEGORIES = [
  'Dairy', 'Retail', 'Textiles', 'Food Processing', 'Poultry',
  'Handicrafts', 'Agri Input Store', 'Tailoring', 'Other',
]

const LANGUAGES = [
  { code: 'en', label: 'English' },
  { code: 'hi', label: 'हिंदी (Hindi)' },
]

export default function InputForm({ form, setForm, onSubmit, loading, showBusinessName = false }) {
  const [ideaText, setIdeaText] = useState('')
  const [ideaLoading, setIdeaLoading] = useState(false)
  const [ideaResult, setIdeaResult] = useState(null)
  const [ideaError, setIdeaError] = useState(null)

  function update(key, value) {
    setForm((prev) => ({ ...prev, [key]: value }))
  }

  async function handleIdeaSuggest() {
    if (!ideaText.trim()) return
    setIdeaLoading(true)
    setIdeaError(null)
    setIdeaResult(null)
    try {
      const suggestion = await getIdeaSuggestion({
        business_idea_description: ideaText,
        available_margin_capital: form.available_margin_capital ? Number(form.available_margin_capital) : null,
      })
      setIdeaResult(suggestion)
      update('business_category', suggestion.detected_business_category)
      if (suggestion.detected_business_category === 'Other' && suggestion.detected_business_category_other) {
        update('business_category_other', suggestion.detected_business_category_other)
      }
      if (!form.available_margin_capital) {
        update('available_margin_capital', String(suggestion.suggested_starting_margin_capital))
      }
      update('business_idea_description', ideaText)
    } catch (err) {
      setIdeaError(err.message || 'Could not read your idea right now — please pick a category below instead.')
    } finally {
      setIdeaLoading(false)
    }
  }

  return (
    <form
      className="panel"
      onSubmit={(e) => { e.preventDefault(); onSubmit() }}
    >
      <div className="field">
        <label htmlFor="language">Answer in which language? / किस भाषा में जवाब चाहिए?</label>
        <select id="language" value={form.language}
          onChange={(e) => update('language', e.target.value)}>
          {LANGUAGES.map((l) => <option key={l.code} value={l.code}>{l.label}</option>)}
        </select>
      </div>

      {showBusinessName && (
        <div className="field">
          <label htmlFor="business_name">Name this business plan</label>
          <input id="business_name" value={form.business_name}
            onChange={(e) => update('business_name', e.target.value)}
            placeholder="e.g. Meena's Dairy" />
          <span className="field-hint">
            Use the same name each time you check in on this business — your
            saved plans will group together as one timeline.
          </span>
        </div>
      )}

      <h3>Not sure what to call your idea? Describe it in your own words</h3>
      <div className="idea-box">
        <textarea
          className="idea-textarea"
          rows={3}
          value={ideaText}
          onChange={(e) => setIdeaText(e.target.value)}
          placeholder="e.g. I have 2 buffaloes and want to sell milk and ghee in my village"
        />
        <button type="button" className="btn btn-secondary" onClick={handleIdeaSuggest} disabled={ideaLoading || !ideaText.trim()}>
          {ideaLoading ? 'Reading your idea…' : '✨ Suggest category for me'}
        </button>
        {ideaResult && (
          <div className="idea-suggestion-note">{ideaResult.explanation}</div>
        )}
        {ideaError && <div className="idea-suggestion-note idea-suggestion-error">{ideaError}</div>}
      </div>

      <h3 style={{ marginTop: 28 }}>1. Where are you starting your business?</h3>
      <div className="field-row">
        <div className="field">
          <label htmlFor="village">Village / Town</label>
          <input id="village" required value={form.village}
            onChange={(e) => update('village', e.target.value)} placeholder="e.g. Bilaspur" />
        </div>
        <div className="field">
          <label htmlFor="block">Block / Tehsil (optional)</label>
          <input id="block" value={form.block}
            onChange={(e) => update('block', e.target.value)} placeholder="e.g. Kota" />
        </div>
      </div>
      <div className="field-row">
        <div className="field">
          <label htmlFor="district">District</label>
          <input id="district" required value={form.district}
            onChange={(e) => update('district', e.target.value)} placeholder="e.g. Kota" />
        </div>
        <div className="field">
          <label htmlFor="state">State</label>
          <input id="state" required value={form.state}
            onChange={(e) => update('state', e.target.value)} placeholder="e.g. Rajasthan" />
        </div>
      </div>
      <div className="field">
        <label htmlFor="pincode">PIN Code (optional, improves accuracy)</label>
        <input id="pincode" value={form.pincode}
          onChange={(e) => update('pincode', e.target.value)} placeholder="6-digit PIN" />
      </div>

      <h3 style={{ marginTop: 28 }}>2. Tell us where you're starting from</h3>
      <p className="field-hint" style={{ marginTop: -8, marginBottom: 12 }}>
        There's no wrong answer here — this just helps us give you the right kind of advice.
      </p>
      <div className="field">
        <label htmlFor="business_stage">Right now, this business is...</label>
        <select id="business_stage" value={form.business_stage}
          onChange={(e) => update('business_stage', e.target.value)}>
          <option value="idea">Just an idea in my head</option>
          <option value="researching">Something I'm looking into / researching</option>
          <option value="ongoing">Already running — I do this today</option>
        </select>
      </div>

      {form.business_stage === 'ongoing' && (
        <div className="field">
          <label htmlFor="current_monthly_revenue">
            Roughly how much money does it bring in per month right now? (₹)
          </label>
          <input id="current_monthly_revenue" type="number" min="0"
            value={form.current_monthly_revenue}
            onChange={(e) => update('current_monthly_revenue', e.target.value)}
            placeholder="e.g. 15000" />
          <span className="field-hint">
            A rough number is fine — this helps us base your report on your real numbers
            instead of a general estimate.
          </span>
        </div>
      )}

      <div className="field">
        <label htmlFor="legal_structure">How is it (or will it be) set up?</label>
        <select id="legal_structure" value={form.legal_structure}
          onChange={(e) => update('legal_structure', e.target.value)}>
          <option value="none_informal">Just me / my family — nothing formal yet</option>
          <option value="proprietorship">Registered in my own name (proprietorship)</option>
          <option value="shg_or_cooperative">Part of a Self-Help Group / cooperative</option>
          <option value="partnership">Partnership with one or more people</option>
          <option value="private_limited">Private Limited Company</option>
          <option value="llp">LLP</option>
          <option value="opc">One Person Company</option>
          <option value="not_sure">Not sure yet</option>
        </select>
        <span className="field-hint">
          Most rural businesses start with "nothing formal yet" — that's completely normal
          and won't stop you from qualifying for a scheme.
        </span>
      </div>

      <h3 style={{ marginTop: 28 }}>3. What can you contribute?</h3>
      <div className="field">
        <label htmlFor="margin">Available margin capital (₹)</label>
        <input id="margin" type="number" min="1" required value={form.available_margin_capital}
          onChange={(e) => update('available_margin_capital', e.target.value)}
          placeholder="e.g. 100000" />
        <span className="field-hint">
          This is your own contribution — typically 10% of total project cost.
        </span>
      </div>

      <h3 style={{ marginTop: 28 }}>4. What business are you planning?</h3>
      <div className="field">
        <label htmlFor="category">Business category</label>
        <select id="category" value={form.business_category}
          onChange={(e) => update('business_category', e.target.value)}>
          {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
        </select>
      </div>
      {form.business_category === 'Other' && (
        <div className="field">
          <label htmlFor="category_other">Describe your business</label>
          <input id="category_other" required value={form.business_category_other}
            onChange={(e) => update('business_category_other', e.target.value)}
            placeholder="e.g. Mobile repair shop" />
          <span className="field-hint">
            Since "Other" doesn't map to one of our standard categories, tell us in a few
            words what it is — this is what shows up in your report instead of just "Other".
          </span>
        </div>
      )}

      <h3 style={{ marginTop: 28 }}>Optional profile details</h3>
      <div className="field-row">
        <div className="field">
          <label htmlFor="age">Age</label>
          <input id="age" type="number" min="18" value={form.applicant_age}
            onChange={(e) => update('applicant_age', e.target.value)} />
        </div>
        <div className="field">
          <label htmlFor="gender">Gender</label>
          <select id="gender" value={form.applicant_gender}
            onChange={(e) => update('applicant_gender', e.target.value)}>
            <option value="">Prefer not to say</option>
            <option value="Female">Female</option>
            <option value="Male">Male</option>
            <option value="Other">Other</option>
          </select>
        </div>
      </div>

      <button type="submit" className="btn btn-primary" disabled={loading} style={{ marginTop: 12 }}>
        {loading ? 'Generating your report…' : 'Generate feasibility report'}
      </button>
    </form>
  )
}
