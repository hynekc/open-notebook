/**
 * Links from the app to the documentation, in the interface language when a
 * translation exists.
 *
 * Czech (cs-CZ) translates the user-facing sections of docs/ into docs/cs/,
 * with the same folder layout and the same anchors. Every other page (and every
 * other language) links to the upstream English documentation.
 */

export const DOCS_BASE_URL = 'https://github.com/lfnovo/open-notebook/blob/main/docs/'

/** Where the Czech help is published. Change it if the fork or branch moves. */
export const CS_DOCS_BASE_URL = 'https://github.com/hynekc/open-notebook/blob/cs-CZ/docs/cs/'

/** Sections of docs/ that are translated into docs/cs/. */
const CS_TRANSLATED_SECTIONS = [
  '0-START-HERE/',
  '2-CORE-CONCEPTS/',
  '3-USER-GUIDE/',
  '4-AI-PROVIDERS/',
  '6-TROUBLESHOOTING/',
]

/**
 * URL of a documentation page.
 *
 * @param path - Path under docs/, with an optional anchor, e.g. '3-USER-GUIDE/api-configuration.md#encryption-setup'
 * @param language - The interface language code (e.g. 'cs-CZ')
 * @param csPath - Optional Czech page to use instead of `path` (also under docs/cs/)
 */
export function docsUrl(path: string, language: string | undefined, csPath?: string): string {
  if (language?.startsWith('cs')) {
    const target = csPath ?? path
    if (target === '' || target === 'index.md' || CS_TRANSLATED_SECTIONS.some(s => target.startsWith(s))) {
      return CS_DOCS_BASE_URL + target
    }
  }
  return DOCS_BASE_URL + path
}
