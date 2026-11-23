/**
 * Map a language code detected from the browser to one of the UI languages.
 *
 * Browsers often report only the base language ("cs", "pl") while the UI
 * resources use region codes ("cs-CZ", "pl-PL"). Without this mapping such a
 * browser falls back to English even though a translation exists.
 *
 * Exact matches win, then a case-insensitive match, then the first resource
 * with the same base language. Anything else is returned unchanged, so
 * i18next's normal fallback applies.
 */
export function toSupportedLanguage(lng: string, supported: readonly string[]): string {
  if (!lng) return lng
  if (supported.includes(lng)) return lng

  const lower = lng.toLowerCase().replace('_', '-')
  const exact = supported.find(code => code.toLowerCase() === lower)
  if (exact) return exact

  const base = lower.split('-')[0]
  const sameBase = supported.find(code => code.toLowerCase().split('-')[0] === base)
  return sameBase ?? lng
}
