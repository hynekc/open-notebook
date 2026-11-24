'use client'

import { useMemo, useState } from 'react'
import { Loader2, Sparkles } from 'lucide-react'
import type { SourceListResponse } from '@/lib/types/api'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Textarea } from '@/components/ui/textarea'
import { useGenerateNote } from '@/lib/hooks/use-notes'
import { useTransformations } from '@/lib/hooks/use-transformations'
import { useTranslation } from '@/lib/hooks/use-translation'

type Mode = 'prompt' | 'transformation'

interface GenerateNoteDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  notebookId: string
  /** Sources loaded in the notebook view (all start selected) */
  sources?: SourceListResponse[]
}

export function GenerateNoteDialog({ open, onOpenChange, notebookId, sources = [] }: GenerateNoteDialogProps) {
  const { t } = useTranslation()
  const generateNote = useGenerateNote()
  const { data: transformations = [] } = useTransformations()

  const [mode, setMode] = useState<Mode>('prompt')
  const [prompt, setPrompt] = useState('')
  const [transformationId, setTransformationId] = useState('')
  const [title, setTitle] = useState('')
  // Sources the user unticked; everything else counts as selected, so sources
  // loaded later (pagination) are included by default
  const [excluded, setExcluded] = useState<string[]>([])

  const selectedIds = useMemo(
    () => sources.map((s) => s.id).filter((id) => !excluded.includes(id)),
    [sources, excluded]
  )
  const allSelected = excluded.length === 0

  const reset = () => {
    setMode('prompt')
    setPrompt('')
    setTransformationId('')
    setTitle('')
    setExcluded([])
  }

  const handleOpenChange = (next: boolean) => {
    // Keep the dialog open while the model works, so the result isn't lost
    if (!next && generateNote.isPending) return
    if (!next) reset()
    onOpenChange(next)
  }

  const toggleSource = (id: string) => {
    setExcluded((current) => (current.includes(id) ? current.filter((x) => x !== id) : [...current, id]))
  }

  const canGenerate =
    sources.length > 0 &&
    selectedIds.length > 0 &&
    !generateNote.isPending &&
    (mode === 'prompt' ? prompt.trim().length > 0 : transformationId.length > 0)

  const handleGenerate = async () => {
    if (!canGenerate) return
    try {
      await generateNote.mutateAsync({
        notebook_id: notebookId,
        // All ticked = let the server take every source of the notebook
        source_ids: allSelected ? undefined : selectedIds,
        ...(mode === 'prompt' ? { prompt: prompt.trim() } : { transformation_id: transformationId }),
        title: title.trim() || undefined,
      })
      reset()
      onOpenChange(false)
    } catch {
      // The hook shows the error toast; keep the dialog so the user can adjust
    }
  }

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-[640px]">
        <DialogHeader>
          <DialogTitle>{t('notebooks.generateNoteTitle')}</DialogTitle>
          <DialogDescription>{t('notebooks.generateNoteDescription')}</DialogDescription>
        </DialogHeader>

        {sources.length === 0 ? (
          <p className="text-sm text-muted-foreground">{t('notebooks.generateNoSources')}</p>
        ) : (
          <div className="space-y-4">
            <Tabs value={mode} onValueChange={(value) => setMode(value as Mode)}>
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="prompt">{t('notebooks.generateFromPrompt')}</TabsTrigger>
                <TabsTrigger value="transformation">{t('notebooks.generateFromTransformation')}</TabsTrigger>
              </TabsList>
              <TabsContent value="prompt" className="mt-3">
                <Label htmlFor="generate-note-prompt" className="mb-2 block">
                  {t('notebooks.generatePromptLabel')}
                </Label>
                <Textarea
                  id="generate-note-prompt"
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder={t('notebooks.generatePromptPlaceholder')}
                  rows={4}
                  maxLength={4000}
                />
              </TabsContent>
              <TabsContent value="transformation" className="mt-3">
                <Label htmlFor="generate-note-transformation" className="mb-2 block">
                  {t('notebooks.generateTransformationLabel')}
                </Label>
                <Select value={transformationId} onValueChange={setTransformationId}>
                  <SelectTrigger id="generate-note-transformation" className="w-full">
                    <SelectValue placeholder={t('notebooks.generateTransformationPlaceholder')} />
                  </SelectTrigger>
                  <SelectContent>
                    {transformations.map((tr) => (
                      <SelectItem key={tr.id} value={tr.id}>
                        {tr.title || tr.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </TabsContent>
            </Tabs>

            <div>
              <div className="mb-2 flex items-center justify-between">
                <Label>{t('notebooks.generateSourcesLabel')}</Label>
                <span className="text-xs text-muted-foreground">
                  {t('notebooks.generateSourcesSelected', { count: selectedIds.length })}
                </span>
              </div>
              <div className="flex items-center gap-2 mb-2">
                <Checkbox
                  id="generate-note-all-sources"
                  checked={allSelected}
                  onCheckedChange={(checked) => setExcluded(checked === true ? [] : sources.map((s) => s.id))}
                />
                <Label htmlFor="generate-note-all-sources" className="text-sm font-normal">
                  {t('notebooks.generateAllSources')}
                </Label>
              </div>
              <ul className="max-h-44 space-y-1 overflow-y-auto rounded-md border border-border p-2">
                {sources.map((source) => {
                  const id = `generate-note-source-${encodeURIComponent(source.id)}`
                  return (
                    <li key={source.id} className="flex items-center gap-2">
                      <Checkbox
                        id={id}
                        checked={!excluded.includes(source.id)}
                        onCheckedChange={() => toggleSource(source.id)}
                      />
                      <Label htmlFor={id} className="truncate text-sm font-normal">
                        {source.title || t('sources.untitledSource')}
                      </Label>
                    </li>
                  )
                })}
              </ul>
            </div>

            <div>
              <Label htmlFor="generate-note-title" className="mb-2 block">
                {t('notebooks.generateNoteTitleLabel')}
              </Label>
              <Input
                id="generate-note-title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder={t('notebooks.generateNoteTitlePlaceholder')}
                maxLength={300}
                autoComplete="off"
              />
            </div>

            {generateNote.isPending && (
              <p className="flex items-center gap-2 text-sm text-teal" role="status">
                <Loader2 className="h-4 w-4 animate-spin" />
                {t('notebooks.generating')}
              </p>
            )}
          </div>
        )}

        <DialogFooter>
          <Button variant="outline" onClick={() => handleOpenChange(false)} disabled={generateNote.isPending}>
            {t('common.cancel')}
          </Button>
          <Button onClick={() => void handleGenerate()} disabled={!canGenerate}>
            {generateNote.isPending ? (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Sparkles className="h-4 w-4 mr-2" />
            )}
            {t('notebooks.generateButton')}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
