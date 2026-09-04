import { createContext, useContext, useEffect, useState } from 'react'

const LanguageContext = createContext(null)

/**
 * Global language state so pages outside the advisory form (Landing, Login,
 * History, the App header/footer) can also be localized. Persists to
 * localStorage so the choice sticks across visits/reloads. InputForm's own
 * language <select> keeps this in sync via setLanguage so the whole app
 * reflects the language chosen for the report.
 */
export function LanguageProvider({ children }) {
  const [language, setLanguageState] = useState(() => {
    try {
      return localStorage.getItem('gv_language') || 'en'
    } catch {
      return 'en'
    }
  })

  function setLanguage(lang) {
    setLanguageState(lang)
    try {
      localStorage.setItem('gv_language', lang)
    } catch {
      // ignore storage errors (private browsing, etc.)
    }
  }

  useEffect(() => {
    try {
      localStorage.setItem('gv_language', language)
    } catch {
      // ignore
    }
  }, [language])

  return (
    <LanguageContext.Provider value={{ language, setLanguage }}>
      {children}
    </LanguageContext.Provider>
  )
}

export function useLanguage() {
  const ctx = useContext(LanguageContext)
  if (!ctx) {
    throw new Error('useLanguage must be used within a LanguageProvider')
  }
  return ctx
}
