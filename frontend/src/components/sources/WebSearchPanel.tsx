"use client"

import { useState } from "react"
import { ExternalLink, Loader2, Search } from "lucide-react"
import { useTranslation } from "@/lib/hooks/use-translation"
import { webSearchApi } from "@/lib/api/web-search"
import { getApiErrorMessage } from "@/lib/utils/error-handler"
import type { WebSearchResult } from "@/lib/types/api"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Checkbox } from "@/components/ui/checkbox"
import { Label } from "@/components/ui/label"

interface WebSearchPanelProps {
  /** Called with the URLs the user picked; the caller adds them as link sources. */
  onAddUrls: (urls: string[]) => void
  /** Most URLs that can still be added (batch limit minus URLs already entered). */
  maxSelectable: number
}

/** Language code for the search engine from the UI language: "cs-CZ" -> "cs". */
export function searchLanguageFor(uiLanguage: string | undefined): string | undefined {
  const base = (uiLanguage || "").split("-")[0].toLowerCase()
  return /^[a-z]{2,3}$/.test(base) ? base : undefined
}

function hostOf(url: string): string {
  try {
    return new URL(url).hostname.replace(/^www\./, "")
  } catch {
    return url
  }
}

export function WebSearchPanel({ onAddUrls, maxSelectable }: WebSearchPanelProps) {
  const { t, language } = useTranslation()
  const [query, setQuery] = useState("")
  const [onlyUiLanguage, setOnlyUiLanguage] = useState(true)
  const [results, setResults] = useState<WebSearchResult[] | null>(null)
  const [selected, setSelected] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const runSearch = async () => {
    const q = query.trim()
    if (!q || loading) return
    setLoading(true)
    setError(null)
    try {
      const response = await webSearchApi.search({
        q,
        language: onlyUiLanguage ? searchLanguageFor(language) : "all",
        limit: 20,
      })
      setResults(response.results)
      setSelected([])
    } catch (err) {
      setError(getApiErrorMessage(err, (key) => t(key), "sources.webSearchFailed"))
      setResults(null)
    } finally {
      setLoading(false)
    }
  }

  const toggle = (url: string) => {
    setSelected((current) =>
      current.includes(url)
        ? current.filter((u) => u !== url)
        : current.length < maxSelectable
          ? [...current, url]
          : current
    )
  }

  const limitReached = selected.length >= maxSelectable

  return (
    <div className="space-y-3">
      <div className="flex gap-2">
        <Input
          aria-label={t("sources.webSearchQueryLabel")}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => {
            // Enter searches instead of submitting the whole wizard form
            if (e.key === "Enter") {
              e.preventDefault()
              void runSearch()
            }
          }}
          placeholder={t("sources.webSearchPlaceholder")}
          maxLength={300}
          autoComplete="off"
        />
        <Button type="button" onClick={() => void runSearch()} disabled={!query.trim() || loading}>
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
          <span className="ml-2">{t("sources.webSearchButton")}</span>
        </Button>
      </div>

      <div className="flex items-center gap-2">
        <Checkbox
          id="web-search-ui-language"
          checked={onlyUiLanguage}
          onCheckedChange={(checked) => setOnlyUiLanguage(checked === true)}
        />
        <Label htmlFor="web-search-ui-language" className="text-xs font-normal text-muted-foreground">
          {t("sources.webSearchOnlyUiLanguage")}
        </Label>
      </div>

      {error && (
        <p role="alert" className="text-sm text-destructive">
          {error}
        </p>
      )}

      {results !== null && results.length === 0 && !error && (
        <p className="text-sm text-muted-foreground">{t("sources.webSearchNoResults")}</p>
      )}

      {results !== null && results.length > 0 && (
        <>
          <ul className="max-h-72 space-y-2 overflow-y-auto pr-1">
            {results.map((result) => {
              const checked = selected.includes(result.url)
              const id = `web-result-${encodeURIComponent(result.url)}`
              return (
                <li
                  key={result.url}
                  className={`rounded-md border p-2 ${checked ? "border-primary bg-primary/5" : "border-border"}`}
                >
                  <div className="flex items-start gap-2">
                    <Checkbox
                      id={id}
                      checked={checked}
                      disabled={!checked && limitReached}
                      onCheckedChange={() => toggle(result.url)}
                      className="mt-0.5"
                    />
                    <div className="min-w-0 flex-1">
                      <Label htmlFor={id} className="block cursor-pointer text-sm font-medium leading-snug">
                        {result.title}
                      </Label>
                      <div className="mt-0.5 flex items-center gap-1 text-xs text-muted-foreground">
                        <span className="truncate">{hostOf(result.url)}</span>
                        <a
                          href={result.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex shrink-0 items-center hover:text-foreground"
                          aria-label={t("sources.webSearchOpenResult")}
                          title={t("sources.webSearchOpenResult")}
                        >
                          <ExternalLink className="h-3 w-3" />
                        </a>
                      </div>
                      {result.snippet && (
                        <p className="mt-1 line-clamp-2 text-xs text-muted-foreground">{result.snippet}</p>
                      )}
                    </div>
                  </div>
                </li>
              )
            })}
          </ul>
          <div className="flex items-center justify-between gap-2">
            <span className="text-xs text-muted-foreground">
              {limitReached
                ? t("sources.webSearchLimitReached", { count: maxSelectable })
                : t("sources.webSearchSelectedCount", { count: selected.length })}
            </span>
            <Button type="button" onClick={() => onAddUrls(selected)} disabled={selected.length === 0}>
              {t("sources.webSearchAddSelected", { count: selected.length })}
            </Button>
          </div>
        </>
      )}
    </div>
  )
}
