'use client'

import { Empty, Grid, List, Magazine } from '@/components/articles/layout'
import { useArticlesPaginationStore } from '@/stores/articles-pagination'
import { useEffect, useMemo } from 'react'

import { useArticles, useUserPreferences } from '@/hooks/api'
import { useArticlePagination } from '@/hooks/features/pagination'
import { useSplitLayout } from '@/hooks/ui/layout'

import type { EmptyTypes } from '@/components/articles/layout/empty'
import type { ArticleListQuery } from '@/types/api'

interface ArticlesContainerProps {
	baseQuery?: Partial<ArticleListQuery>
	emptyType: string
}

export default function ArticlesContainer({
	baseQuery: propBaseQuery,
	emptyType
}: ArticlesContainerProps) {
	const { data: preferences } = useUserPreferences()
	const { shouldShowSplitLayout } = useSplitLayout()

	const {
		q,
		is_read,
		read_later,
		folderOptions,
		subscriptionOptions,
		tagOptions,
		from_date,
		to_date,
		isRefreshing
	} = useArticlesPaginationStore()

	const storeBaseQuery = useMemo(() => {
		const query: Partial<ArticleListQuery> = {}

		if (q) query.q = q
		if (is_read !== 'all') query.is_read = is_read
		if (read_later !== 'all') query.read_later = read_later
		if (folderOptions.length > 0)
			query.folder_ids = folderOptions.map((o) => o.value)
		if (subscriptionOptions.length > 0)
			query.subscription_ids = subscriptionOptions.map((o) => o.value)
		if (tagOptions.length > 0) query.tag_ids = tagOptions.map((o) => o.value)
		if (from_date) query.from_date = from_date
		if (to_date) query.to_date = to_date

		return query
	}, [
		q,
		is_read,
		read_later,
		folderOptions,
		subscriptionOptions,
		tagOptions,
		from_date,
		to_date
	])

	// Use prop query if provided (for specific pages like feeds/folders/read/unread)
	// Otherwise use store filters (for /articles page)
	const baseQuery = useMemo(() => {
		// If prop baseQuery is provided with actual keys, use it
		if (propBaseQuery && Object.keys(propBaseQuery).length > 0) {
			return propBaseQuery
		}
		return storeBaseQuery
	}, [storeBaseQuery, propBaseQuery])

	const isUsingPropQuery = Boolean(
		propBaseQuery && Object.keys(propBaseQuery).length > 0
	)
	useEffect(() => {
		if (isUsingPropQuery) {
			const { resetFilters } = useArticlesPaginationStore.getState()
			resetFilters()
		}
	}, [isUsingPropQuery])

	const articlePagination = useArticlePagination(
		baseQuery ? { baseQuery } : undefined
	)

	const {
		articles,
		initialQuery,
		initializeWithData,
		isItemLoaded,
		itemCount,
		loadMoreItems
	} = articlePagination

	const { data: articlesData, isLoading: articlesLoading } =
		useArticles(initialQuery)

	useEffect(() => {
		if (articlesData) {
			initializeWithData(articlesData, isRefreshing)
		}
	}, [articlesData, initializeWithData, isRefreshing])

	if (!preferences) {
		return null
	}

	if (articles.length > 0 || articlesLoading || isRefreshing) {
		const loading = articlesLoading || isRefreshing
		return (
			<div className='space-y-4'>
				{preferences?.article_layout === 'grid' && (
					<Grid
						articles={articles}
						itemCount={itemCount}
						loadMoreItems={loadMoreItems}
						loading={loading}
						splitLayout={shouldShowSplitLayout}
					/>
				)}
				{preferences?.article_layout === 'list' && (
					<List
						articles={articles}
						isItemLoaded={isItemLoaded}
						itemCount={itemCount}
						loadMoreItems={loadMoreItems}
						loading={loading}
					/>
				)}
				{preferences?.article_layout === 'magazine' && (
					<Magazine
						articles={articles}
						isItemLoaded={isItemLoaded}
						itemCount={itemCount}
						loadMoreItems={loadMoreItems}
						loading={loading}
					/>
				)}
			</div>
		)
	}

	return <Empty type={emptyType as EmptyTypes} />
}
