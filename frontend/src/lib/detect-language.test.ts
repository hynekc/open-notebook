import { describe, it, expect } from 'vitest'
import { toSupportedLanguage } from './detect-language'

const SUPPORTED = ['en-US', 'cs-CZ', 'pl-PL', 'zh-CN', 'zh-TW', 'pt-BR'] as const

describe('toSupportedLanguage', () => {
  it('keeps supported codes', () => {
    expect(toSupportedLanguage('cs-CZ', SUPPORTED)).toBe('cs-CZ')
    expect(toSupportedLanguage('zh-TW', SUPPORTED)).toBe('zh-TW')
  })

  it('maps a base language to its regional resource', () => {
    expect(toSupportedLanguage('cs', SUPPORTED)).toBe('cs-CZ')
    expect(toSupportedLanguage('pl', SUPPORTED)).toBe('pl-PL')
    expect(toSupportedLanguage('pt', SUPPORTED)).toBe('pt-BR')
  })

  it('matches case-insensitively and with underscores', () => {
    expect(toSupportedLanguage('cs-cz', SUPPORTED)).toBe('cs-CZ')
    expect(toSupportedLanguage('cs_CZ', SUPPORTED)).toBe('cs-CZ')
  })

  it('maps another region of a supported language', () => {
    expect(toSupportedLanguage('en-GB', SUPPORTED)).toBe('en-US')
  })

  it('leaves unsupported languages to the i18next fallback', () => {
    expect(toSupportedLanguage('sk', SUPPORTED)).toBe('sk')
    expect(toSupportedLanguage('', SUPPORTED)).toBe('')
  })
})
