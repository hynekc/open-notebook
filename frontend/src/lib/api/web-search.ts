import apiClient from './client'
import type { WebSearchResponse } from '@/lib/types/api'

export interface WebSearchParams {
  q: string
  language?: string
  page?: number
  limit?: number
}

export const webSearchApi = {
  /**
   * Search the web for new sources through the server's SearXNG instance.
   * Only available when GET /capabilities reports web_search_available.
   */
  search: async (params: WebSearchParams): Promise<WebSearchResponse> => {
    const response = await apiClient.get<WebSearchResponse>('/web-search', { params })
    return response.data
  },
}
