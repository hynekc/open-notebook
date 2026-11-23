import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import LanguageDetector from 'i18next-browser-languagedetector'
import { resources } from './locales'
import { toSupportedLanguage } from './detect-language'

const supportedLanguages = Object.keys(resources)

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'en-US',
    interpolation: {
      escapeValue: false, // react already safes from xss
    },
    react: {
      useSuspense: false,
    },
    detection: {
      order: ['localStorage', 'navigator'],
      caches: ['localStorage'],
      // Browsers often report only "cs" or "pl"; map them to "cs-CZ", "pl-PL".
      convertDetectedLanguage: (lng: string) => toSupportedLanguage(lng, supportedLanguages),
    },
  })

export default i18n
