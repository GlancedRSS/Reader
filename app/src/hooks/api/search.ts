import { useStaticSWR } from '@/lib/swr-config'

import type {
	FeedSearchQuery,
	FeedSearchResponse,
	FolderSearchQuery,
	FolderSearchResponse,
	TagSearchQuery,
	TagSearchResponse,
	UnifiedSearchQuery,
	UnifiedSearchResponse
} from '@/types/api'
import type { QueryValue } from '@/utils/query'

import { buildQueryParams } from '@/utils/query'

const searchSWRConfig = {
	errorRetryCount: 0,
	shouldRetryOnError: false
} as const

export function useUnifiedSearch(params?: UnifiedSearchQuery) {
	const queryString = buildQueryParams(
		(params || {}) as Record<string, QueryValue>
	)
	const url = queryString ? `/search?${queryString}` : null

	return useStaticSWR<UnifiedSearchResponse>(url, searchSWRConfig)
}

export function useFeedSearch(params?: FeedSearchQuery) {
	const queryString = buildQueryParams(
		(params || {}) as Record<string, QueryValue>
	)
	const url = queryString ? `/search/feeds?${queryString}` : null

	return useStaticSWR<FeedSearchResponse>(url, searchSWRConfig)
}

export function useTagSearch(params?: TagSearchQuery) {
	const queryString = buildQueryParams(
		(params || {}) as Record<string, QueryValue>
	)
	const url = queryString ? `/search/tags?${queryString}` : null

	return useStaticSWR<TagSearchResponse>(url, searchSWRConfig)
}

export function useFolderSearch(params?: FolderSearchQuery) {
	const queryString = buildQueryParams(
		(params || {}) as Record<string, QueryValue>
	)
	const url = queryString ? `/search/folders?${queryString}` : null

	return useStaticSWR<FolderSearchResponse>(url, searchSWRConfig)
}
