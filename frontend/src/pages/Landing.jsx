import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'
import { useLanguage } from '../LanguageContext.jsx'
import { t } from '../i18n.js'

export default function Landing() {
  const { isLoggedIn } = useAuth()
  const { language } = useLanguage()
  const navigate = useNavigate()

  function choosePersonal() {
    navigate(isLoggedIn ? '/advisor/personal' : '/login')
  }

  return (
    <>
      <section className="hero-split container">
        <div className="hero-copy">
          <h1 dangerouslySetInnerHTML={{ __html: t(language, 'landing.heroHeading') }} />
          <p>{t(language, 'landing.heroParagraph')}</p>
          <div className="hero-ctas">
            <button className="btn btn-primary" onClick={choosePersonal}>
              {isLoggedIn ? t(language, 'landing.goToMyPlan') : t(language, 'landing.loginSignup')}
            </button>
            <Link to="/advisor/open" className="btn btn-secondary">
              {t(language, 'landing.useWithoutAccount')}
            </Link>
          </div>
        </div>

        <div className="hero-stats-card">
          <div className="stat">
            <div className="stat-value">10%</div>
            <div className="stat-label">{t(language, 'landing.marginContribution')}</div>
          </div>
          <div className="stat">
            <div className="stat-value">90%</div>
            <div className="stat-label">{t(language, 'landing.concessionalLoan')}</div>
          </div>
          <div className="stat">
            <div className="stat-value">{t(language, 'landing.schemesChecked')}</div>
            <div className="stat-label">{t(language, 'landing.schemesCheckedDesc')}</div>
          </div>
        </div>
      </section>

      <section className="section container">
        <div className="section-head">
          <h2>{t(language, 'landing.howToUse')}</h2>
        </div>
        <div className="use-case-grid">
          <div className="use-case-card">
            <h4>{t(language, 'landing.personalTitle')}</h4>
            <p>{t(language, 'landing.personalDesc')}</p>
            <button className="btn btn-primary" onClick={choosePersonal}>
              {isLoggedIn ? t(language, 'landing.goToMyPlan') : t(language, 'landing.loginSignup')}
            </button>
          </div>
          <div className="use-case-card">
            <h4>{t(language, 'landing.openTitle')}</h4>
            <p>{t(language, 'landing.openDesc')}</p>
            <Link to="/advisor/open" className="btn btn-secondary">
              {t(language, 'landing.useWithoutAccount')}
            </Link>
          </div>
        </div>
      </section>
    </>
  )
}
