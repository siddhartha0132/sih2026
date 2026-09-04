import SchemesList from './SchemesList.jsx'
import { t } from '../i18n.js'

function formatINR(n) {
  return `₹${Number(n).toLocaleString('en-IN')}`
}

export default function FinancialPlanCard({ plan, language = 'en' }) {
  const ineligible = plan.selected_scheme.startsWith('Not Eligible')

  return (
    <div className="panel">
      <h2>{t(language, 'financial.title')}</h2>

      {plan.warnings.length > 0 && (
        <div className="error-box">
          {plan.warnings.map((w) => <p key={w} style={{ margin: 0 }}>{w}</p>)}
        </div>
      )}

      <div className="stat-row">
        <div className="stat">
          <div className="stat-value">{formatINR(plan.project_cost)}</div>
          <div className="stat-label">{t(language, 'financial.totalProjectCost')}</div>
        </div>
        <div className="stat">
          <div className="stat-value">{formatINR(plan.max_loan_amount)}</div>
          <div className="stat-label">{t(language, 'financial.maxLoanEligibility')}</div>
        </div>
        <div className="stat">
          <div className="stat-value">{plan.selected_scheme}</div>
          <div className="stat-label">{t(language, 'financial.matchedScheme')}</div>
        </div>
      </div>

      <p>{plan.scheme_explanation}</p>
      {plan.official_source_url && (
        <p className="confidence-note">
          {t(language, 'financial.officialTerms')}{' '}
          <a href={plan.official_source_url} target="_blank" rel="noopener noreferrer">
            {plan.official_source_url}
          </a>{' '}
          {t(language, 'financial.verifiedOn', { date: plan.terms_verified_on })}
        </p>
      )}

      {!ineligible && (
        <>
          <div className="stat-row">
            <div className="stat">
              <div className="stat-value">{plan.interest_rate_percent}%</div>
              <div className="stat-label">{t(language, 'financial.interestRate')}</div>
            </div>
            <div className="stat">
              <div className="stat-value">{plan.tenure_years}y / {plan.moratorium_months}m</div>
              <div className="stat-label">{t(language, 'financial.tenureMoratorium')}</div>
            </div>
            <div className="stat">
              <div className="stat-value">{formatINR(plan.quarterly_installment_amount)}</div>
              <div className="stat-label">{t(language, 'financial.quarterlyInstallment')}</div>
            </div>
          </div>

          <div className="stat-row" style={{ gridTemplateColumns: '1fr 1fr' }}>
            <div className="stat">
              <div className="stat-value">{formatINR(plan.total_interest_payable)}</div>
              <div className="stat-label">{t(language, 'financial.totalInterestPayable')}</div>
            </div>
            <div className="stat">
              <div className="stat-value">{formatINR(plan.total_repayable)}</div>
              <div className="stat-label">{t(language, 'financial.totalRepayable')}</div>
            </div>
          </div>

          <h3 style={{ marginTop: 24 }}>{t(language, 'financial.repaymentSchedule')}</h3>
          <div style={{ overflowX: 'auto' }}>
            <table className="schedule">
              <thead>
                <tr>
                  <th>{t(language, 'financial.table.period')}</th>
                  <th>{t(language, 'financial.table.openingBalance')}</th>
                  <th>{t(language, 'financial.table.principal')}</th>
                  <th>{t(language, 'financial.table.interest')}</th>
                  <th>{t(language, 'financial.table.installment')}</th>
                  <th>{t(language, 'financial.table.closingBalance')}</th>
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

      <SchemesList schemes={plan.all_schemes} language={language} />
    </div>
  )
}
