import { create } from 'zustand'

import type { ArticleListResponse } from '@/types/api'

type SelectOption = {
	label: string
	value: string
}

interface ArticlesPaginationState {
	allArticles: ArticleListResponse[]
	currentCursor: string | undefined
	currentQuery: string | null
	hasMore: boolean
	isInitialized: boolean
	isLoadingMore: boolean
	isRefreshing: boolean
	canRetry: boolean
	q: string
	is_read: 'all' | 'read' | 'unread'
	read_later: 'all' | 'true' | 'false'
	folderOptions: SelectOption[]
	subscriptionOptions: SelectOption[]
	tagOptions: SelectOption[]
	from_date: string
	to_date: string

	setAllArticles: (articles: ArticleListResponse[]) => void
	addArticles: (articles: ArticleListResponse[]) => void
	setCurrentCursor: (cursor: string | undefined) => void
	setCurrentQuery: (query: string | null) => void
	setHasMore: (hasMore: boolean) => void
	setIsInitialized: (initialized: boolean) => void
	setIsLoadingMore: (loading: boolean) => void
	setIsRefreshing: (refreshing: boolean) => void
	setCanRetry: (canRetry: boolean) => void
	reset: () => void
	refreshArticles: () => void
	markArticleAsRead: (articleId: string) => void

	setQ: (q: string) => void
	setIsRead: (is_read: 'all' | 'read' | 'unread') => void
	setReadLater: (read_later: 'all' | 'true' | 'false') => void
	setFolderOptions: (options: SelectOption[]) => void
	setSubscriptionOptions: (options: SelectOption[]) => void
	setTagOptions: (options: SelectOption[]) => void
	setFromDate: (from_date: string) => void
	setToDate: (to_date: string) => void
	resetFilters: () => void
}

export const useArticlesPaginationStore = create<ArticlesPaginationState>(
	(set) => ({
		addArticles: (articles) =>
			set((state) => ({ allArticles: [...state.allArticles, ...articles] })),
		allArticles: [],
		canRetry: false,
		currentCursor: undefined,
		currentQuery: null,
		folderOptions: [],
		from_date: '',
		hasMore: true,
		isInitialized: false,
		isLoadingMore: false,
		isRefreshing: false,
		is_read: 'all',
		markArticleAsRead: (articleId) =>
			set((state) => ({
				allArticles: state.allArticles.map((article) =>
					article.id === articleId ? { ...article, is_read: true } : article
				)
			})),
		q: '',
		read_later: 'all',
		refreshArticles: () =>
			set({
				canRetry: false,
				currentCursor: undefined,
				hasMore: true,
				isInitialized: true,
				isLoadingMore: false,
				isRefreshing: true
			}),
		reset: () =>
			set({
				allArticles: [],
				canRetry: false,
				currentCursor: undefined,
				currentQuery: null,
				hasMore: true,
				isInitialized: false,
				isLoadingMore: false,
				isRefreshing: false
			}),

		resetFilters: () =>
			set({
				folderOptions: [],
				from_date: '',
				is_read: 'all',
				q: '',
				read_later: 'all',
				subscriptionOptions: [],
				tagOptions: [],
				to_date: ''
			}),

		setAllArticles: (allArticles) => set({ allArticles }),

		setCanRetry: (canRetry) => set({ canRetry }),

		setCurrentCursor: (currentCursor) => set({ currentCursor }),
		setCurrentQuery: (currentQuery) => set({ currentQuery }),
		setFolderOptions: (folderOptions) => set({ folderOptions }),
		setFromDate: (from_date) => set({ from_date }),

		setHasMore: (hasMore) => set({ hasMore }),
		setIsInitialized: (isInitialized) => set({ isInitialized }),
		setIsLoadingMore: (isLoadingMore) => set({ isLoadingMore }),
		setIsRead: (is_read) => set({ is_read }),
		setIsRefreshing: (isRefreshing) => set({ isRefreshing }),
		setQ: (q) => set({ q }),
		setReadLater: (read_later) => set({ read_later }),
		setSubscriptionOptions: (subscriptionOptions) =>
			set({ subscriptionOptions }),
		setTagOptions: (tagOptions) => set({ tagOptions }),
		setToDate: (to_date) => set({ to_date }),
		subscriptionOptions: [],
		tagOptions: [],
		to_date: ''
	})
)
