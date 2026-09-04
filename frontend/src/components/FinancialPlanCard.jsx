import SchemesList from './SchemesList.jsx'

function formatINR(n) {
  return `₹${Number(n).toLocaleString('en-IN')}`
}

export default function FinancialPlanCard({ plan }) {
  const ineligible = plan.selected_scheme.startsWith('Not Eligible')

  return (
    <div className="panel">
      <h2>Financial plan &amp; scheme match</h2>

      {plan.warnings.length > 0 && (
        <div className="error-box">
          {plan.warnings.map((w) => <p key={w} style={{ margin: 0 }}>{w}</p>)}
        </div>
      )}

      <div className="stat-row">
        <div className="stat">
          <div className="stat-value">{formatINR(plan.project_cost)}</div>
          <div className="stat-label">Total project cost</div>
        </div>
        <div className="stat">
          <div className="stat-value">{formatINR(plan.max_loan_amount)}</div>
          <div className="stat-label">Maximum loan eligibility</div>
        </div>
        <div className="stat">
          <div className="stat-value">{plan.selected_scheme}</div>
          <div className="stat-label">Matched scheme</div>
        </div>
      </div>

      <p>{plan.scheme_explanation}</p>
      {plan.official_source_url && (
        <p className="confidence-note">
          Official scheme terms:{' '}
          <a href={plan.official_source_url} target="_blank" rel="noopener noreferrer">
            {plan.official_source_url}
          </a>{' '}
          (verified {plan.terms_verified_on})
        </p>
      )}

      {!ineligible && (
        <>
          <div className="stat-row">
            <div className="stat">
              <div className="stat-value">{plan.interest_rate_percent}%</div>
              <div className="stat-label">Interest rate (p.a.)</div>
            </div>
            <div className="stat">
              <div className="stat-value">{plan.tenure_years}y / {plan.moratorium_months}m</div>
              <div className="stat-label">Tenure / moratorium</div>
            </div>
            <div className="stat">
              <div className="stat-value">{formatINR(plan.quarterly_installment_amount)}</div>
              <div className="stat-label">Quarterly installment (post-moratorium)</div>
            </div>
          </div>

          <div className="stat-row" style={{ gridTemplateColumns: '1fr 1fr' }}>
            <div className="stat">
              <div className="stat-value">{formatINR(plan.total_interest_payable)}</div>
              <div className="stat-label">Total interest payable</div>
            </div>
            <div className="stat">
              <div className="stat-value">{formatINR(plan.total_repayable)}</div>
              <div className="stat-label">Total repayable (principal + interest)</div>
            </div>
          </div>

          <h3 style={{ marginTop: 24 }}>Repayment schedule</h3>
          <div style={{ overflowX: 'auto' }}>
            <table className="schedule">
              <thead>
                <tr>
                  <th>Period</th>
                  <th>Opening balance</th>
                  <th>Principal</th>
                  <th>Interest</th>
                  <th>Installment</th>
                  <th>Closing balance</th>
                </tr>
              </thead>
              <tbody>
                {plan.repayment_schedule.map((row) => (
                  <tr key={row.period_label}>
                    <td>{row.period_label}</td>
                    <td>{formatINR(row.opening_balance)}</td>
                    <td>{formatINR(row.principal_component)}</td>
                    <td>{formatINR(row.interest_component)}</td>
                    <td>{formatINR(row.installment_amount)}</td>
                    <td>{formatINR(row.closing_balance)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      <SchemesList schemes={plan.all_schemes} />
    </div>
  )
}
