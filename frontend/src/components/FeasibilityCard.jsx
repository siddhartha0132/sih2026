function ConfidenceBadge({ level }) {
  const cls = level === 'High' ? 'badge-high' : level === 'Medium' ? 'badge-medium' : 'badge-low'
  return <span className={`badge ${cls}`}>{level} confidence</span>
}

/** Renders a data_source string as a clickable citation when a source_url is present. */
function SourceLine({ label, url }) {
  return (
    <p className="confidence-note">
      Source:{' '}
      {url ? (
        <a href={url} target="_blank" rel="noopener noreferrer">{label}</a>
      ) : (
        label
      )}
    </p>
  )
}

export default function FeasibilityCard({ report }) {
  const { market_reach, opportunity_analysis, swot, threats, competitor_mapping, pricing } = report

  return (
    <div className="panel" style={{ marginBottom: 24 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', flexWrap: 'wrap', gap: 12 }}>
        <h2>Business feasibility report</h2>
        <ConfidenceBadge level={report.overall_confidence} />
      </div>

      <div className="stat-row">
        <div className="stat">
          <div className="stat-value">{report.business_opportunity_score}/100</div>
          <div className="stat-label">Business opportunity score</div>
        </div>
        <div className="stat">
          <div className="stat-value">{market_reach.estimated_consumer_base.toLocaleString('en-IN')}</div>
          <div className="stat-label">Estimated consumers within {market_reach.radius_km} km</div>
        </div>
        <div className="stat">
          <div className="stat-value">{competitor_mapping.density_rating}</div>
          <div className="stat-label">Competitor density nearby</div>
        </div>
      </div>

      <p>{report.narrative_summary}</p>

      <h3 style={{ marginTop: 24 }}>Market reach</h3>
      <p className="field-hint">Primary distribution channels for this category:</p>
      <ul className="list-clean">
        {market_reach.primary_distribution_channels.map((c) => <li key={c}>{c}</li>)}
      </ul>
      <SourceLine label={market_reach.data_source} url={market_reach.source_url} />

      <h3 style={{ marginTop: 24 }}>Opportunity analysis</h3>
      <ul className="list-clean">
        {opportunity_analysis.underserved_niches.map((n) => <li key={n}>{n}</li>)}
      </ul>
      <p className="field-hint">{opportunity_analysis.rationale}</p>

      <h3 style={{ marginTop: 24 }}>Competitor mapping</h3>
      <p>
        Approximately <strong>{competitor_mapping.estimated_similar_businesses_nearby}</strong> similar
        businesses nearby ({competitor_mapping.density_rating.toLowerCase()} density)
        {competitor_mapping.nearest_competitor_distance_km != null && (
          <> — nearest estimated at {competitor_mapping.nearest_competitor_distance_km} km.</>
        )}
      </p>
      <SourceLine label={competitor_mapping.data_source} url={competitor_mapping.source_url} />

      <h3 style={{ marginTop: 24 }}>SWOT analysis</h3>
      <div className="swot-grid">
        <div className="swot-box">
          <h4>Strengths</h4>
          <ul className="list-clean">{swot.strengths.map((s) => <li key={s}>{s}</li>)}</ul>
        </div>
        <div className="swot-box">
          <h4>Weaknesses</h4>
          <ul className="list-clean">{swot.weaknesses.map((s) => <li key={s}>{s}</li>)}</ul>
        </div>
        <div className="swot-box">
          <h4>Opportunities</h4>
          <ul className="list-clean">{swot.opportunities.map((s) => <li key={s}>{s}</li>)}</ul>
        </div>
        <div className="swot-box">
          <h4>Threats</h4>
          <ul className="list-clean">{swot.threats.map((s) => <li key={s}>{s}</li>)}</ul>
        </div>
      </div>

      <h3 style={{ marginTop: 24 }}>Threats &amp; mitigation</h3>
      <ul className="list-clean">
        {threats.map((t) => (
          <li key={t.threat}>
            <strong>{t.threat}</strong> ({t.severity}) — {t.mitigation}
          </li>
        ))}
      </ul>

      <h3 style={{ marginTop: 24 }}>Suggested pricing / product market value</h3>
      <p>
        Recommended price band: <strong>₹{pricing.suggested_price_range_min}–{pricing.suggested_price_range_max} {pricing.unit}</strong>.
        Predicted local market value: ₹{pricing.predicted_local_market_value} {pricing.unit}.
      </p>
      <p className="field-hint">{pricing.pricing_rationale}</p>
      <SourceLine label={pricing.data_source} url={pricing.source_url} />

      <h3 style={{ marginTop: 24 }}>Actionable next steps</h3>
      <ul className="list-clean">
        {report.actionable_next_steps.map((s) => <li key={s}>{s}</li>)}
      </ul>
    </div>
  )
}
