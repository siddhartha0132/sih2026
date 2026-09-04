import { t } from '../i18n.js'

function formatINR(n) {
  return `₹${Number(n).toLocaleString('en-IN')}`
}

/**
 * The "full truth" revenue view - shows a real low/mid/high range plus
 * operating cost and net income, not a single optimistic number, and always
 * surfaces the explicit downside-risk note alongside the numbers.
 */
export default function RevenueProjectionCard({ projection, language = 'en' }) {
  if (!projection) return null

  return (
    <div className="panel" style={{ marginBottom: 24 }}>
      <h2>{t(language, 'revenue.title')}</h2>
      {projection.used_applicant_reported_revenue && (
        <p className="field-hint">{t(language, 'revenue.basedOnReported')}</p>
      )}

      <div className="stat-row">
        <div className="stat">
          <div className="stat-value">{formatINR(projection.monthly_revenue_low)}</div>
          <div className="stat-label">{t(language, 'revenue.lowMonth')}</div>
        </div>
        <div className="stat">
          <div className="stat-value">{formatINR(projection.monthly_revenue_mid)}</div>
          <div className="stat-label">{t(language, 'revenue.typicalMonth')}</div>
        </div>
        <div className="stat">
          <div className="stat-value">{formatINR(projection.monthly_revenue_high)}</div>
          <div className="stat-label">{t(language, 'revenue.goodMonth')}</div>
        </div>
      </div>

      <div className="stat-row" style={{ gridTemplateColumns: '1fr 1fr' }}>
        <div className="stat">
          <div className="stat-value">{formatINR(projection.monthly_operating_cost_estimate)}</div>
          <div className="stat-label">{t(language, 'revenue.operatingCost')}</div>
        </div>
        <div className="stat">
          <div className="stat-value">{formatINR(projection.monthly_net_income_estimate)}</div>
          <div className="stat-label">{t(language, 'revenue.takeHome')}</div>
        </div>
      </div>

      <h3 style={{ marginTop: 20 }}>{t(language, 'revenue.dealingWith')}</h3>
      <div className="stat-row" style={{ gridTemplateColumns: 'repeat(3, 1fr)' }}>
        <div className="stat">
          <div className="stat-value">{projection.estimated_active_customers}</div>
          <div className="stat-label">{t(language, 'revenue.activeCustomers')}</div>
        </div>
        <div className="stat">
          <div className="stat-value">{projection.estimated_distributors_or_buyers}</div>
          <div className="stat-label">{t(language, 'revenue.distributorsBuyers')}</div>
        </div>
        <div className="stat">
          <div className="stat-value">{projection.estimated_raw_material_sources}</div>
          <div className="stat-label">{t(language, 'revenue.rawMaterialSources')}</div>
        </div>
      </div>

      <div className="field-row" style={{ marginTop: 16 }}>
        <div>
          <p className="field-hint" style={{ marginBottom: 4 }}><strong>{t(language, 'revenue.rawMaterialFrom')}</strong></p>
          <ul className="list-clean">
            {projection.raw_material_source_examples.map((s) => <li key={s}>{s}</li>)}
          </ul>
        </div>
        <div>
          <p className="field-hint" style={{ marginBottom: 4 }}><strong>{t(language, 'revenue.sellDistribute')}</strong></p>
          <ul className="list-clean">
            {projection.distributor_examples.map((s) => <li key={s}>{s}</li>)}
          </ul>
        </div>
      </div>

      <div className="disclaimer" style={{ marginTop: 20 }}>
        {projection.downside_risk_note}
      </div>

      <p className="confidence-note" style={{ marginTop: 12 }}>
        {t(language, 'revenue.methodology')} {projection.methodology}
      </p>
      <p className="confidence-note">
        {t(language, 'common.source')}{' '}
        {projection.source_url ? (
          <a href={projection.source_url} target="_blank" rel="noopener noreferrer">{projection.data_source}</a>
        ) : projection.data_source}
      </p>
    </div>
  )
}
