import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'

export default function Landing() {
  const { isLoggedIn } = useAuth()
  const navigate = useNavigate()

  function choosePersonal() {
    navigate(isLoggedIn ? '/advisor/personal' : '/login')
  }

  return (
    <>
      <section className="section container">
        <h1>Know your market. Know your loan.<br />Before you borrow a rupee.</h1>
        <p>
          GramVyapaar AI turns three simple inputs — your village, your available
          capital, and your business idea — into a hyper-local feasibility report
          and an exact financial roadmap: project cost, loan eligibility, scheme
          match, and repayment schedule.
        </p>
      </section>

      <section className="section container">
        <h2>How do you want to use it?</h2>
        <div className="swot-grid" style={{ marginTop: 20 }}>
          <div className="swot-box">
            <h4>Personal use</h4>
            <p>
              For your own business plan. Log in to save every report, and come
              back later to see how your plan and numbers evolve as your
              business grows.
            </p>
            <div style={{ marginTop: 16 }}>
              <button className="btn btn-primary" onClick={choosePersonal}>
                {isLoggedIn ? 'Go to my plan' : 'Log in / Sign up'}
              </button>
            </div>
          </div>
          <div className="swot-box">
            <h4>Open use</h4>
            <p>
              Try it instantly for anyone — no account, nothing saved. Enter
              your details, get your feasibility report and financial plan
              right away.
            </p>
            <div style={{ marginTop: 16 }}>
              <Link to="/advisor/open" className="btn btn-secondary">
                Use without an account
              </Link>
            </div>
          </div>
        </div>
      </section>

      <section className="section container">
        <div className="stat-row">
          <div className="stat">
            <div className="stat-value">10%</div>
            <div className="stat-label">Your margin money contribution</div>
          </div>
          <div className="stat">
            <div className="stat-value">90%</div>
            <div className="stat-label">Concessional loan from the Channelizing Agency</div>
          </div>
          <div className="stat">
            <div className="stat-value">3 schemes</div>
            <div className="stat-label">Micro Finance (≤₹1.4L), SUVIDHA (≤₹10L) or UTKARSH (≤₹50L), auto-selected</div>
          </div>
        </div>
      </section>
    </>
  )
}
