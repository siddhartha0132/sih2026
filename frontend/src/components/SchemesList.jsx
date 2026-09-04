function formatINR(n) {
  return `₹${Number(n).toLocaleString('en-IN')}`
}

/**
 * Shows EVERY scheme evaluated for this project, not just the one the
 * calculator built a detailed EMI schedule for. Eligible schemes are shown
 * first (recommended one on top), ineligible ones follow, greyed out, with
 * a plain reason why - so the applicant sees every real door, not just one.
 */
export default function SchemesList({ schemes }) {
  if (!schemes || schemes.length === 0) return null

  const sorted = [...schemes].sort((a, b) => {
    if (a.is_recommended !== b.is_recommended) return a.is_recommended ? -1 : 1
    if (a.is_eligible !== b.is_eligible) return a.is_eligible ? -1 : 1
    return 0
  })

  return (
    <div style={{ marginTop: 28 }}>
      <h3>Every scheme you might qualify for</h3>
      <p className="field-hint" style={{ marginBottom: 16 }}>
        This tool builds a full repayment schedule for one scheme above, but you're not limited
        to it - here's every major government scheme checked against your numbers.
      </p>
      <div className="schemes-grid">
        {sorted.map((s) => (
          <div key={s.scheme_name} className={`scheme-card ${s.is_eligible ? 'scheme-eligible' : 'scheme-ineligible'}`}>
            <div className="scheme-card-header">
              <span className="scheme-name">{s.scheme_name}</span>
              {s.is_recommended && <span className="badge badge-high">Recommended</span>}
              {!s.is_recommended && s.is_eligible && <span className="badge badge-medium">Eligible</span>}
              {!s.is_eligible && <span className="badge badge-low">Not a fit</span>}
            </div>
            <p className="scheme-agency">{s.operating_agency}</p>
            <p>{s.description}</p>
            <p className="field-hint">{s.eligibility_note}</p>
            {s.is_eligible && (
              <div className="scheme-terms">
                <span>Loan up to {formatINR(s.max_loan_amount)}</span>
                <span>{s.interest_rate_percent_range}</span>
                <span>Tenure: {s.tenure_years} yrs</span>
              </div>
            )}
            {s.is_eligible && s.subsidy_or_margin_money_note && (
              <p className="field-hint" style={{ marginTop: 8 }}>💰 {s.subsidy_or_margin_money_note}</p>
            )}
            <p className="confidence-note">
              Source:{' '}
              <a href={s.official_source_url} target="_blank" rel="noopener noreferrer">
                {s.official_source_url}
              </a>{' '}
              (verified {s.terms_verified_on})
            </p>
          </div>
        ))}
      </div>
    </div>
  )
}

