import type { ComponentProps } from 'react'
import { render, screen } from '@testing-library/react'
import { useForm, type Control } from 'react-hook-form'
import { describe, expect, it } from 'vitest'
import { SourceTypeStep } from './SourceTypeStep'

// The form shape SourceTypeStep expects (its interface isn't exported)
type FormValues = ComponentProps<typeof SourceTypeStep>['control'] extends Control<infer T> ? T : never

function UploadStep() {
  const { control, register, setValue, formState: { errors } } = useForm<FormValues>({
    defaultValues: { type: 'upload', embed: false, async_processing: false },
  })
  return <SourceTypeStep control={control} register={register} setValue={setValue} errors={errors} />
}

describe('SourceTypeStep', () => {
  it('does not offer archive files in the upload picker', () => {
    render(<UploadStep />)

    const accept = screen.getByLabelText('sources.fileLabel').getAttribute('accept') ?? ''
    const extensions = accept.split(',')

    expect(extensions).not.toContain('.zip')
    expect(extensions).not.toContain('.tar')
    expect(extensions).not.toContain('.gz')
    expect(extensions).toContain('.pdf')
  })
})

function LinkStep({ webSearchAvailable, startWithSearch }: { webSearchAvailable: boolean; startWithSearch?: boolean }) {
  const { control, register, setValue, watch, formState: { errors } } = useForm<FormValues>({
    defaultValues: { type: 'link', url: '', embed: false, async_processing: false },
  })
  return (
    <>
      <SourceTypeStep
        control={control}
        register={register}
        setValue={setValue}
        errors={errors}
        webSearchAvailable={webSearchAvailable}
        startWithSearch={startWithSearch}
      />
      <output data-testid="url-value">{watch('url')}</output>
      <output data-testid="type-value">{watch('type')}</output>
    </>
  )
}

describe('SourceTypeStep web search tab', () => {
  it('is hidden when the server has no web search', () => {
    render(<LinkStep webSearchAvailable={false} />)
    expect(screen.queryByRole('tab', { name: /sources.searchWeb/ })).toBeNull()
  })

  it('opens on the search tab and keeps the form type as link', () => {
    render(<LinkStep webSearchAvailable startWithSearch />)
    const tab = screen.getByRole('tab', { name: /sources.searchWeb/ })
    expect(tab.getAttribute('aria-selected')).toBe('true')
    expect(screen.getByText('sources.webSearchDescription')).toBeTruthy()
    expect(screen.getByTestId('type-value').textContent).toBe('link')
  })
})
