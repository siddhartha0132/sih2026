import { t, densityLabel, confidenceLabel } from '../i18n.js'

function ConfidenceBadge({ level, language }) {
  const cls = level === 'High' ? 'badge-high' : level === 'Medium' ? 'badge-medium' : 'badge-low'
  return <span className={`badge ${cls}`}>{t(language, 'feasibility.confidence', { level: confidenceLabel(language, level) })}</span>
}

/** Renders a data_source string as a clickable citation when a source_url is present. */
function SourceLine({ label, url, language }) {
  return (
    <p className="confidence-note">
      {t(language, 'common.source')}{' '}
      {url ? (
        <a href={url} target="_blank" rel="noopener noreferrer">{label}</a>
      ) : (
        label
      )}
    </p>
  )
}

export default function FeasibilityCard({ report, language = 'en' }) {
  const { market_reach, opportunity_analysis, swot, threats, competitor_mapping, pricing } = report

  return (
    <div className="panel" style={{ marginBottom: 24 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', flexWrap: 'wrap', gap: 12 }}>
        <h2>{t(language, 'feasibility.title')}</h2>
        <ConfidenceBadge level={report.overall_confidence} language={language} />
      </div>

      <div className="stat-row">
        <div className="stat">
          <div className="stat-value">{report.business_opportunity_score}/100</div>
          <div className="stat-label">{t(language, 'feasibility.opportunityScore')}</div>
        </div>
        <div className="stat">
          <div className="stat-value">{market_reach.estimated_consumer_base.toLocaleString('en-IN')}</div>
          <div className="stat-label">{t(language, 'feasibility.consumersWithin', { km: market_reach.radius_km })}</div>
        </div>
        <div className="stat">
          <div className="stat-value">{densityLabel(language, competitor_mapping.density_rating)}</div>
          <div className="stat-label">{t(language, 'feasibility.competitorDensity')}</div>
        </div>
      </div>

      <p>{report.narrative_summary}</p>

      <h3 style={{ marginTop: 24 }}>{t(language, 'feasibility.marketReach')}</h3>
      <p className="field-hint">{t(language, 'feasibility.distributionChannels')}</p>
      <ul className="list-clean">
        {market_reach.primary_distribution_channels.map((c) => <li key={c}>{c}</li>)}
      </ul>
      <SourceLine label={market_reach.data_source} url={market_reach.source_url} language={language} />

      <h3 style={{ marginTop: 24 }}>{t(language, 'feasibility.opportunityAnalysis')}</h3>
      <ul className="list-clean">
        {opportunity_analysis.underserved_niches.map((n) => <li key={n}>{n}</li>)}
      </ul>
      <p className="field-hint">{opportunity_analysis.rationale}</p>

      <h3 style={{ marginTop: 24 }}>{t(language, 'feasibility.competitorMapping')}</h3>
      <p>
        {t(language, 'feasibility.approximately')} <strong>{competitor_mapping.estimated_similar_businesses_nearby}</strong>{' '}
        {t(language, 'feasibility.similarBusinessesNearby')}{' '}
        {t(language, 'feasibility.densitySuffix', { density: densityLabel(language, competitor_mapping.density_rating) })}
        {competitor_mapping.nearest_competitor_distance_km != null && (
          <> {t(language, 'feasibility.nearestCompetitor', { km: competitor_mapping.nearest_competitor_distance_km })}</>
        )}
      </p>
      <SourceLine label={competitor_mapping.data_source} url={competitor_mapping.source_url} language={language} />

      <h3 style={{ marginTop: 24 }}>{t(language, 'feasibility.swot')}</h3>
      <div className="swot-grid">
        <div className="swot-box">
          <h4>{t(language, 'feasibility.strengths')}</h4>
          <ul className="list-clean">{swot.strengths.map((s) => <li key={s}>{s}</li>)}</ul>
        </div>
        <div className="swot-box">
          <h4>{t(language, 'feasibility.weaknesses')}</h4>
          <ul className="list-clean">{swot.weaknesses.map((s) => <li key={s}>{s}</li>)}</ul>
        </div>
        <div className="swot-box">
          <h4>{t(language, 'feasibility.opportunities')}</h4>
          <ul className="list-clean">{swot.opportunities.map((s) => <li key={s}>{s}</li>)}</ul>
        </div>
        <div className="swot-box">
          <h4>{t(language, 'feasibility.threats')}</h4>
          <ul className="list-clean">{swot.threats.map((s) => <li key={s}>{s}</li>)}</ul>
        </div>
      </div>

      <h3 style={{ marginTop: 24 }}>{t(language, 'feasibility.threatsAndMitigation')}</h3>
      <ul className="list-clean">
        {threats.map((t2) => (
          <li key={t2.threat}>
            <strong>{t2.threat}</strong> ({t2.severity}) — {t2.mitigation}
          </li>
        ))}
      </ul>

      <h3 style={{ marginTop: 24 }}>{t(language, 'feasibility.pricingTitle')}</h3>
      <p>
        {t(language, 'feasibility.recommendedPriceBand')} <strong>₹{pricing.suggested_price_range_min}–{pricing.suggested_price_range_max} {pricing.unit}</strong>.{' '}
        {t(language, 'feasibility.predictedMarketValue')} ₹{pricing.predicted_local_market_value} {pricing.unit}.
      </p>
      <p className="field-hint">{pricing.pricing_rationale}</p>
      <SourceLine label={pricing.data_source} url={pricing.source_url} language={language} />

      <h3 style={{ marginTop: 24 }}>{t(language, 'feasibility.nextSteps')}</h3>
      <ul className="list-clean">
        {report.actionable_next_steps.map((s) => <li key={s}>{s}</li>)}
      </ul>
    </div>
  )
}
