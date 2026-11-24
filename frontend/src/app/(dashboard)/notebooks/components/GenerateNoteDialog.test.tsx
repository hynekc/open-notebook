import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { GenerateNoteDialog } from './GenerateNoteDialog'
import type { SourceListResponse } from '@/lib/types/api'

const mutateAsync = vi.fn()
vi.mock('@/lib/hooks/use-notes', () => ({
  useGenerateNote: () => ({ mutateAsync, isPending: false }),
}))
vi.mock('@/lib/hooks/use-transformations', () => ({
  useTransformations: () => ({ data: [{ id: 'transformation:1', name: 'dense', title: 'Husté shrnutí' }] }),
}))
vi.mock('@/lib/hooks/use-translation', () => ({
  useTranslation: () => ({ t: (key: string) => key, language: 'cs-CZ' }),
}))

const SOURCES = [
  { id: 'source:a', title: 'Rybníky' },
  { id: 'source:b', title: 'Třeboňsko' },
] as SourceListResponse[]

function renderDialog(sources = SOURCES) {
  const onOpenChange = vi.fn()
  render(<GenerateNoteDialog open onOpenChange={onOpenChange} notebookId="notebook:1" sources={sources} />)
  return { onOpenChange }
}

describe('GenerateNoteDialog', () => {
  beforeEach(() => {
    mutateAsync.mockReset()
    mutateAsync.mockResolvedValue({ id: 'note:1' })
  })

  it('generates from a question over all sources and closes', async () => {
    const { onOpenChange } = renderDialog()
    const generate = screen.getByRole('button', { name: /notebooks.generateButton/ })
    expect(generate).toBeDisabled()

    fireEvent.change(screen.getByLabelText('notebooks.generatePromptLabel'), {
      target: { value: '  Shrň rybníky  ' },
    })
    fireEvent.click(generate)

    await waitFor(() => expect(onOpenChange).toHaveBeenCalledWith(false))
    expect(mutateAsync).toHaveBeenCalledWith({
      notebook_id: 'notebook:1',
      source_ids: undefined,
      prompt: 'Shrň rybníky',
      title: undefined,
    })
  })

  it('sends only the ticked sources and the title', async () => {
    renderDialog()
    fireEvent.click(screen.getByLabelText('Rybníky'))
    fireEvent.change(screen.getByLabelText('notebooks.generatePromptLabel'), { target: { value: 'Otázky' } })
    fireEvent.change(screen.getByLabelText('notebooks.generateNoteTitleLabel'), { target: { value: 'Moje' } })
    fireEvent.click(screen.getByRole('button', { name: /notebooks.generateButton/ }))

    await waitFor(() => expect(mutateAsync).toHaveBeenCalled())
    expect(mutateAsync.mock.calls[0][0]).toMatchObject({ source_ids: ['source:b'], title: 'Moje' })
  })

  it('cannot generate with no source ticked', () => {
    renderDialog()
    fireEvent.click(screen.getByLabelText('notebooks.generateAllSources'))
    fireEvent.change(screen.getByLabelText('notebooks.generatePromptLabel'), { target: { value: 'Otázky' } })
    expect(screen.getByRole('button', { name: /notebooks.generateButton/ })).toBeDisabled()
  })

  it('keeps the dialog open when generation fails', async () => {
    mutateAsync.mockRejectedValue(new Error('boom'))
    const { onOpenChange } = renderDialog()
    fireEvent.change(screen.getByLabelText('notebooks.generatePromptLabel'), { target: { value: 'x' } })
    fireEvent.click(screen.getByRole('button', { name: /notebooks.generateButton/ }))
    await waitFor(() => expect(mutateAsync).toHaveBeenCalled())
    expect(onOpenChange).not.toHaveBeenCalled()
  })

  it('explains that sources are needed first', () => {
    renderDialog([])
    expect(screen.getByText('notebooks.generateNoSources')).toBeTruthy()
    expect(screen.getByRole('button', { name: /notebooks.generateButton/ })).toBeDisabled()
  })
})
