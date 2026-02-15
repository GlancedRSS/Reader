import { useArticlesPaginationStore } from '@/stores/articles-pagination'
import { useCallback, useMemo, useRef } from 'react'
import { toast } from 'sonner'

import { apiClient } from '@/lib/api'

import type {
	ArticleListQuery,
	ArticleListResponse,
	PaginatedResponse
} from '@/types/api'

import { buildQueryParams } from '@/utils/query'

interface UseInfiniteArticlesOptions {
	baseQuery?: Partial<ArticleListQuery>
	limit?: number
}

export function useArticlePagination(options: UseInfiniteArticlesOptions = {}) {
	const { baseQuery = {} } = options

	const {
		allArticles,
		currentCursor,
		currentQuery,
		hasMore,
		isInitialized,
		isLoadingMore,
		isRefreshing,
		canRetry,
		setAllArticles,
		addArticles,
		setCurrentCursor,
		setCurrentQuery,
		setHasMore,
		setIsInitialized,
		setIsLoadingMore,
		setIsRefreshing,
		setCanRetry,
		reset
	} = useArticlesPaginationStore()

	const retryCountRef = useRef(0)

	const serializedBaseQuery = useMemo(
		() => JSON.stringify(baseQuery),
		[baseQuery]
	)

	const initialQuery = useMemo(
		() => ({
			...baseQuery,
			limit: 24
		}),
		[baseQuery]
	)

	const loadMoreQuery = useMemo(
		() => ({
			...baseQuery,
			cursor: currentCursor,
			limit: 24
		}),
		[baseQuery, currentCursor]
	)

	const isItemLoaded = useCallback(
		(index: number) => {
			return index < allArticles.length
		},
		[allArticles.length]
	)

	const itemCount =
		hasMore && currentCursor ? allArticles.length + 1 : allArticles.length

	const loadMoreItems = useCallback(async () => {
		if (
			!currentCursor ||
			!hasMore ||
			!isInitialized ||
			isLoadingMore ||
			canRetry
		)
			return

		setIsLoadingMore(true)
		setCanRetry(false)

		try {
			const queryString = buildQueryParams(loadMoreQuery)
			const url = `/articles?${queryString}`
			const response =
				await apiClient.get<PaginatedResponse<ArticleListResponse>>(url)

			addArticles(response.data.data)
			setHasMore(response.data.pagination.has_more ?? false)
			setCurrentCursor(response.data.pagination.next_cursor ?? undefined)
			retryCountRef.current = 0
			setCanRetry(false)
			setIsLoadingMore(false)
		} catch (error) {
			console.error('Error loading more articles:', error)

			retryCountRef.current += 1

			if (retryCountRef.current <= 1) {
				toast.info('Retrying to load more articles...')

				await new Promise((resolve) => setTimeout(resolve, 1000))

				return loadMoreItems()
			} else {
				setIsLoadingMore(false)
				setCanRetry(true)
				toast.error('Failed to load more articles. Please try again.', {
					action: {
						label: 'Retry',
						onClick: retryLoadMore
					},
					classNames: {
						actionButton:
							'!bg-primary/85 !text-primary-foreground !shadow-lg !shadow-black/5 dark:!shadow-white/10 hover:!bg-primary/95 hover:!shadow-xl hover:!shadow-black/10 dark:hover:!shadow-white/20 active:!scale-[0.98] active:!shadow-md !border !border-white/10 dark:!border-white/5'
					},
					duration: 10000
				})
			}
		}
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, [
		currentCursor,
		hasMore,
		isInitialized,
		loadMoreQuery,
		isLoadingMore,
		canRetry,
		addArticles,
		setHasMore,
		setCurrentCursor,
		setIsLoadingMore,
		setCanRetry
	])

	const retryLoadMore = useCallback(() => {
		retryCountRef.current = 0
		setCanRetry(false)
		loadMoreItems()
	}, [loadMoreItems, setCanRetry])

	const initializeWithData = useCallback(
		(
			data: PaginatedResponse<ArticleListResponse>,
			isRefreshingParam?: boolean
		) => {
			const currentRefreshing = isRefreshingParam ?? isRefreshing
			const queryChanged = currentQuery !== serializedBaseQuery

			const shouldPreserveState =
				!currentRefreshing &&
				isInitialized &&
				allArticles.length > 0 &&
				!queryChanged

			if (shouldPreserveState) {
				setHasMore(data.pagination.has_more ?? false)
			} else {
				setAllArticles(data.data)
				setHasMore(data.pagination.has_more ?? false)
				setCurrentCursor(data.pagination.next_cursor ?? undefined)
				setCurrentQuery(serializedBaseQuery)
				setIsInitialized(true)
				setIsRefreshing(false)
			}
		},
		[
			allArticles.length,
			currentQuery,
			isInitialized,
			isRefreshing,
			serializedBaseQuery,
			setAllArticles,
			setCurrentCursor,
			setCurrentQuery,
			setHasMore,
			setIsInitialized,
			setIsRefreshing
		]
	)

	return {
		articles: allArticles,
		initialQuery,
		initializeWithData,
		isInitialized,
		isItemLoaded,
		itemCount,
		loadMoreItems,
		reset
	}
}
