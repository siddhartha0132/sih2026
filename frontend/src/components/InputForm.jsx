import { useState } from 'react'
import { getIdeaSuggestion } from '../api/client.js'
import { LANGUAGES, t, categoryLabel } from '../i18n.js'
import { useLanguage } from '../LanguageContext.jsx'

const CATEGORIES = [
  'Dairy', 'Retail', 'Textiles', 'Food Processing', 'Poultry',
  'Handicrafts', 'Agri Input Store', 'Tailoring', 'Other',
]

export default function InputForm({ form, setForm, onSubmit, loading, showBusinessName = false }) {
  const { setLanguage } = useLanguage()
  const lang = form.language
  const [ideaText, setIdeaText] = useState('')
  const [ideaLoading, setIdeaLoading] = useState(false)
  const [ideaResult, setIdeaResult] = useState(null)
  const [ideaError, setIdeaError] = useState(null)

  function update(key, value) {
    setForm((prev) => ({ ...prev, [key]: value }))
    if (key === 'language') setLanguage(value)
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
        language: form.language,
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
      setIdeaError(err.message || t(lang, 'form.ideaErrorFallback'))
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
        <label htmlFor="language">{t(lang, 'form.languageLabel')}</label>
        <select id="language" value={form.language}
          onChange={(e) => update('language', e.target.value)}>
          {LANGUAGES.map((l) => <option key={l.code} value={l.code}>{l.label}</option>)}
        </select>
      </div>

      {showBusinessName && (
        <div className="field">
          <label htmlFor="business_name">{t(lang, 'form.businessNameLabel')}</label>
          <input id="business_name" value={form.business_name}
            onChange={(e) => update('business_name', e.target.value)}
            placeholder={t(lang, 'form.businessNamePlaceholder')} />
          <span className="field-hint">
            {t(lang, 'form.businessNameHint')}
          </span>
        </div>
      )}

      <h3>{t(lang, 'form.ideaSectionTitle')}</h3>
      <div className="idea-box">
        <textarea
          className="idea-textarea"
          rows={3}
          value={ideaText}
          onChange={(e) => setIdeaText(e.target.value)}
          placeholder={t(lang, 'form.ideaPlaceholder')}
        />
        <button type="button" className="btn btn-secondary" onClick={handleIdeaSuggest} disabled={ideaLoading || !ideaText.trim()}>
          {ideaLoading ? t(lang, 'form.ideaLoading') : t(lang, 'form.ideaSuggestButton')}
        </button>
        {ideaResult && (
          <div className="idea-suggestion-note">{ideaResult.explanation}</div>
        )}
        {ideaError && <div className="idea-suggestion-note idea-suggestion-error">{ideaError}</div>}
      </div>

      <h3 style={{ marginTop: 28 }}>{t(lang, 'form.section1')}</h3>
      <div className="field-row">
        <div className="field">
          <label htmlFor="village">{t(lang, 'form.village')}</label>
          <input id="village" required value={form.village}
            onChange={(e) => update('village', e.target.value)} placeholder={t(lang, 'form.villagePlaceholder')} />
        </div>
        <div className="field">
          <label htmlFor="block">{t(lang, 'form.block')}</label>
          <input id="block" value={form.block}
            onChange={(e) => update('block', e.target.value)} placeholder={t(lang, 'form.blockPlaceholder')} />
        </div>
      </div>
      <div className="field-row">
        <div className="field">
          <label htmlFor="district">{t(lang, 'form.district')}</label>
          <input id="district" required value={form.district}
            onChange={(e) => update('district', e.target.value)} placeholder={t(lang, 'form.districtPlaceholder')} />
        </div>
        <div className="field">
          <label htmlFor="state">{t(lang, 'form.state')}</label>
          <input id="state" required value={form.state}
            onChange={(e) => update('state', e.target.value)} placeholder={t(lang, 'form.statePlaceholder')} />
        </div>
      </div>
      <div className="field">
        <label htmlFor="pincode">{t(lang, 'form.pincode')}</label>
        <input id="pincode" value={form.pincode}
          onChange={(e) => update('pincode', e.target.value)} placeholder={t(lang, 'form.pincodePlaceholder')} />
      </div>

      <h3 style={{ marginTop: 28 }}>{t(lang, 'form.section2')}</h3>
      <p className="field-hint" style={{ marginTop: -8, marginBottom: 12 }}>
        {t(lang, 'form.section2Hint')}
      </p>
      <div className="field">
        <label htmlFor="business_stage">{t(lang, 'form.businessStageLabel')}</label>
        <select id="business_stage" value={form.business_stage}
          onChange={(e) => update('business_stage', e.target.value)}>
          <option value="idea">{t(lang, 'form.stage.idea')}</option>
          <option value="researching">{t(lang, 'form.stage.researching')}</option>
          <option value="ongoing">{t(lang, 'form.stage.ongoing')}</option>
        </select>
      </div>

      {form.business_stage === 'ongoing' && (
        <div className="field">
          <label htmlFor="current_monthly_revenue">
            {t(lang, 'form.currentRevenueLabel')}
          </label>
          <input id="current_monthly_revenue" type="number" min="0"
            value={form.current_monthly_revenue}
            onChange={(e) => update('current_monthly_revenue', e.target.value)}
            placeholder={t(lang, 'form.currentRevenuePlaceholder')} />
          <span className="field-hint">
            {t(lang, 'form.currentRevenueHint')}
          </span>
        </div>
      )}

      <div className="field">
        <label htmlFor="legal_structure">{t(lang, 'form.legalStructureLabel')}</label>
        <select id="legal_structure" value={form.legal_structure}
          onChange={(e) => update('legal_structure', e.target.value)}>
          <option value="none_informal">{t(lang, 'form.legal.none_informal')}</option>
          <option value="proprietorship">{t(lang, 'form.legal.proprietorship')}</option>
          <option value="shg_or_cooperative">{t(lang, 'form.legal.shg_or_cooperative')}</option>
          <option value="partnership">{t(lang, 'form.legal.partnership')}</option>
          <option value="private_limited">{t(lang, 'form.legal.private_limited')}</option>
          <option value="llp">{t(lang, 'form.legal.llp')}</option>
          <option value="opc">{t(lang, 'form.legal.opc')}</option>
          <option value="not_sure">{t(lang, 'form.legal.not_sure')}</option>
        </select>
        <span className="field-hint">
          {t(lang, 'form.legalStructureHint')}
        </span>
      </div>

      <h3 style={{ marginTop: 28 }}>{t(lang, 'form.section3')}</h3>
      <div className="field">
        <label htmlFor="margin">{t(lang, 'form.marginLabel')}</label>
        <input id="margin" type="number" min="1" required value={form.available_margin_capital}
          onChange={(e) => update('available_margin_capital', e.target.value)}
          placeholder={t(lang, 'form.marginPlaceholder')} />
        <span className="field-hint">
          {t(lang, 'form.marginHint')}
        </span>
      </div>

      <h3 style={{ marginTop: 28 }}>{t(lang, 'form.section4')}</h3>
      <div className="field">
        <label htmlFor="category">{t(lang, 'form.categoryLabel')}</label>
        <select id="category" value={form.business_category}
          onChange={(e) => update('business_category', e.target.value)}>
          {CATEGORIES.map((c) => <option key={c} value={c}>{categoryLabel(lang, c)}</option>)}
        </select>
      </div>
      {form.business_category === 'Other' && (
        <div className="field">
          <label htmlFor="category_other">{t(lang, 'form.categoryOtherLabel')}</label>
          <input id="category_other" required value={form.business_category_other}
            onChange={(e) => update('business_category_other', e.target.value)}
            placeholder={t(lang, 'form.categoryOtherPlaceholder')} />
          <span className="field-hint">
            {t(lang, 'form.categoryOtherHint')}
          </span>
        </div>
      )}

      <h3 style={{ marginTop: 28 }}>{t(lang, 'form.optionalProfile')}</h3>
      <div className="field-row">
        <div className="field">
          <label htmlFor="age">{t(lang, 'form.age')}</label>
          <input id="age" type="number" min="18" value={form.applicant_age}
            onChange={(e) => update('applicant_age', e.target.value)} />
        </div>
        <div className="field">
          <label htmlFor="gender">{t(lang, 'form.gender')}</label>
          <select id="gender" value={form.applicant_gender}
            onChange={(e) => update('applicant_gender', e.target.value)}>
            <option value="">{t(lang, 'form.gender.notSay')}</option>
            <option value="Female">{t(lang, 'form.gender.female')}</option>
            <option value="Male">{t(lang, 'form.gender.male')}</option>
            <option value="Other">{t(lang, 'form.gender.other')}</option>
          </select>
        </div>
      </div>

      <button type="submit" className="btn btn-primary" disabled={loading} style={{ marginTop: 12 }}>
        {loading ? t(lang, 'form.generating') : t(lang, 'form.submit')}
      </button>
    </form>
  )
}
