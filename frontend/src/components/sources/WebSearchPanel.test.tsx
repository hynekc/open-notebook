import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { WebSearchPanel, searchLanguageFor } from './WebSearchPanel'
import { webSearchApi } from '@/lib/api/web-search'

vi.mock('@/lib/api/web-search', () => ({ webSearchApi: { search: vi.fn() } }))
vi.mock('@/lib/hooks/use-translation', () => ({
  useTranslation: () => ({
    t: (key: string, opts?: { count?: number }) => (opts?.count !== undefined ? `${key}:${opts.count}` : key),
    language: 'cs-CZ',
  }),
}))

const mockSearch = vi.mocked(webSearchApi.search)

const RESULTS = {
  query: 'rybník',
  results: [
    { title: 'Rybník – Wikipedie', url: 'https://cs.wikipedia.org/wiki/Rybnik', snippet: 'Umělá nádrž' },
    { title: 'Rybníkářství', url: 'https://www.example.cz/rybnikarstvi', snippet: '' },
    { title: 'Třeboňsko', url: 'https://example.org/trebon', snippet: 'Rybníky na jihu' },
  ],
}

async function searchFor(text: string) {
  fireEvent.change(screen.getByLabelText('sources.webSearchQueryLabel'), { target: { value: text } })
  fireEvent.click(screen.getByRole('button', { name: /sources.webSearchButton/ }))
  await waitFor(() => expect(screen.getByText('Rybník – Wikipedie')).toBeTruthy())
}

describe('searchLanguageFor', () => {
  it('maps UI locales to search languages', () => {
    expect(searchLanguageFor('cs-CZ')).toBe('cs')
    expect(searchLanguageFor('zh-TW')).toBe('zh')
    expect(searchLanguageFor(undefined)).toBeUndefined()
    expect(searchLanguageFor('')).toBeUndefined()
  })
})

describe('WebSearchPanel', () => {
  beforeEach(() => {
    mockSearch.mockReset()
  })

  it('searches in the UI language and adds the picked URLs', async () => {
    mockSearch.mockResolvedValue(RESULTS)
    const onAddUrls = vi.fn()
    render(<WebSearchPanel onAddUrls={onAddUrls} maxSelectable={50} />)

    await searchFor('  rybník ')
    expect(mockSearch).toHaveBeenCalledWith({ q: 'rybník', language: 'cs', limit: 20 })

    fireEvent.click(screen.getByLabelText('Rybník – Wikipedie'))
    fireEvent.click(screen.getByLabelText('Třeboňsko'))
    fireEvent.click(screen.getByRole('button', { name: 'sources.webSearchAddSelected:2' }))

    expect(onAddUrls).toHaveBeenCalledWith([
      'https://cs.wikipedia.org/wiki/Rybnik',
      'https://example.org/trebon',
    ])
  })

  it('searches all languages when the language filter is off', async () => {
    mockSearch.mockResolvedValue(RESULTS)
    render(<WebSearchPanel onAddUrls={vi.fn()} maxSelectable={50} />)
    fireEvent.click(screen.getByLabelText('sources.webSearchOnlyUiLanguage'))
    await searchFor('rybník')
    expect(mockSearch).toHaveBeenCalledWith({ q: 'rybník', language: 'all', limit: 20 })
  })

  it('does not let the selection exceed the remaining batch limit', async () => {
    mockSearch.mockResolvedValue(RESULTS)
    const onAddUrls = vi.fn()
    render(<WebSearchPanel onAddUrls={onAddUrls} maxSelectable={1} />)
    await searchFor('rybník')

    fireEvent.click(screen.getByLabelText('Rybník – Wikipedie'))
    fireEvent.click(screen.getByLabelText('Třeboňsko'))
    expect(screen.getByText('sources.webSearchLimitReached:1')).toBeTruthy()
    fireEvent.click(screen.getByRole('button', { name: 'sources.webSearchAddSelected:1' }))
    expect(onAddUrls).toHaveBeenCalledWith(['https://cs.wikipedia.org/wiki/Rybnik'])
  })

  it('shows the API error', async () => {
    mockSearch.mockRejectedValue({ response: { data: { detail: 'The search engine is not reachable' } } })
    render(<WebSearchPanel onAddUrls={vi.fn()} maxSelectable={50} />)
    fireEvent.change(screen.getByLabelText('sources.webSearchQueryLabel'), { target: { value: 'x' } })
    fireEvent.click(screen.getByRole('button', { name: /sources.webSearchButton/ }))
    await waitFor(() => expect(screen.getByRole('alert').textContent).toBe('The search engine is not reachable'))
  })

  it('Enter in the query field searches instead of submitting a form', async () => {
    // Radix checkboxes inside a <form> measure themselves with ResizeObserver
    vi.stubGlobal('ResizeObserver', class { observe() {} unobserve() {} disconnect() {} })
    mockSearch.mockResolvedValue(RESULTS)
    const onSubmit = vi.fn((e: { preventDefault: () => void }) => e.preventDefault())
    render(
      <form onSubmit={onSubmit}>
        <WebSearchPanel onAddUrls={vi.fn()} maxSelectable={50} />
      </form>
    )
    const input = screen.getByLabelText('sources.webSearchQueryLabel')
    fireEvent.change(input, { target: { value: 'rybník' } })
    fireEvent.keyDown(input, { key: 'Enter' })
    await waitFor(() => expect(mockSearch).toHaveBeenCalled())
    expect(onSubmit).not.toHaveBeenCalled()
  })
})
