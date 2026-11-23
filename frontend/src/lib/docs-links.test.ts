import { describe, it, expect } from 'vitest'
import { docsUrl, DOCS_BASE_URL, CS_DOCS_BASE_URL } from './docs-links'

describe('docsUrl', () => {
  it('links to the English docs for non-Czech languages', () => {
    expect(docsUrl('3-USER-GUIDE/api-configuration.md#encryption-setup', 'en-US')).toBe(
      DOCS_BASE_URL + '3-USER-GUIDE/api-configuration.md#encryption-setup',
    )
    expect(docsUrl('3-USER-GUIDE/search.md', 'pl-PL')).toBe(DOCS_BASE_URL + '3-USER-GUIDE/search.md')
    expect(docsUrl('3-USER-GUIDE/search.md', undefined)).toBe(DOCS_BASE_URL + '3-USER-GUIDE/search.md')
  })

  it('links to the Czech help for translated sections', () => {
    expect(docsUrl('3-USER-GUIDE/api-configuration.md#encryption-setup', 'cs-CZ')).toBe(
      CS_DOCS_BASE_URL + '3-USER-GUIDE/api-configuration.md#encryption-setup',
    )
    expect(docsUrl('6-TROUBLESHOOTING/index.md', 'cs')).toBe(CS_DOCS_BASE_URL + '6-TROUBLESHOOTING/index.md')
  })

  it('keeps untranslated sections in English for Czech', () => {
    expect(docsUrl('5-CONFIGURATION/security.md', 'cs-CZ')).toBe(DOCS_BASE_URL + '5-CONFIGURATION/security.md')
  })

  it('uses the Czech override page when given', () => {
    expect(
      docsUrl('5-CONFIGURATION/ai-providers.md', 'cs-CZ', '4-AI-PROVIDERS/index.md#connect-a-provider'),
    ).toBe(CS_DOCS_BASE_URL + '4-AI-PROVIDERS/index.md#connect-a-provider')
    expect(docsUrl('5-CONFIGURATION/ai-providers.md', 'en-US', '4-AI-PROVIDERS/index.md')).toBe(
      DOCS_BASE_URL + '5-CONFIGURATION/ai-providers.md',
    )
  })
})
