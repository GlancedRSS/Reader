import GridLoading from '@/components/articles/layout/grid/loading'
import { GridRow } from '@/components/articles/layout/grid/row'
import {
	useRowHeightCache,
	useVirtualizedList
} from '@/components/articles/layout/hooks'
import { memo, useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { List } from 'react-window'

import { useUserPreferences } from '@/hooks/api'

import { ArticleListResponse } from '@/types/api'

const SCROLL_TO_ARTICLE_KEY = 'scroll-to-article-id'

function ArticleGrid({
	articles,
	loading,
	itemCount,
	loadMoreItems,
	splitLayout = false
}: {
	articles: ArticleListResponse[]
	loading: boolean
	itemCount: number
	loadMoreItems: () => Promise<void>
	splitLayout?: boolean
}) {
	const { data: preferences } = useUserPreferences()

	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	const listRef = useRef<any>(null)
	const hasScrolledToTarget = useRef(false)

	const defaultHeight = useMemo(() => {
		const SHOW_THUMBNAIL_HEIGHT = 192
		const SHOW_SUMMARY_HEIGHT = 52
		const BASE_HEIGHT = 128

		let height = BASE_HEIGHT

		if (preferences?.show_article_thumbnails) {
			height += SHOW_THUMBNAIL_HEIGHT
		}

		if (preferences?.show_summaries) {
			height += SHOW_SUMMARY_HEIGHT
		}

		return height
	}, [preferences])

	const { getRowHeight, setRowHeight, clearCacheIfNeeded } = useRowHeightCache({
		defaultHeight
	})

	const [windowWidth, setWindowWidth] = useState(0)

	useEffect(() => {
		const handleResize = () => setWindowWidth(window.innerWidth)
		handleResize()
		window.addEventListener('resize', handleResize)
		return () => window.removeEventListener('resize', handleResize)
	}, [])

	const columns = useMemo(() => {
		if (splitLayout) {
			return 1
		}

		if (windowWidth >= 1600) return 4
		if (windowWidth >= 1280) return 3
		if (windowWidth >= 640) return 2
		return 1
	}, [windowWidth, splitLayout])

	const totalRows = Math.ceil(itemCount / columns)

	const isRowLoaded = useCallback(
		(rowIndex: number) => {
			const startIndex = rowIndex * columns
			const endIndex = startIndex + columns
			for (let i = startIndex; i < endIndex; i++) {
				if (i >= articles.length || !articles[i]) {
					return false
				}
			}
			return true
		},
		[articles, columns]
	)

	const { onRowsRendered } = useVirtualizedList({
		isItemLoaded: isRowLoaded,
		itemCount: totalRows,
		loadMoreItems,
		threshold: 6
	})

	clearCacheIfNeeded(articles.length)

	useEffect(() => {
		if (hasScrolledToTarget.current || loading || articles.length === 0) {
			return
		}

		const savedArticleId = sessionStorage.getItem(SCROLL_TO_ARTICLE_KEY)
		if (!savedArticleId) {
			return
		}

		const index = articles.findIndex((a) => a?.id === savedArticleId)
		if (index !== -1 && index < articles.length && listRef.current) {
			const rowIndex = Math.floor(index / columns)
			setTimeout(() => {
				if (listRef.current) {
					listRef.current.scrollToRow({
						align: 'start',
						behavior: 'smooth',
						index: rowIndex
					})
					hasScrolledToTarget.current = true
					sessionStorage.removeItem(SCROLL_TO_ARTICLE_KEY)
				}
			}, 100)
		}
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, [loading, articles.length, columns])

	const rowProps = useMemo(
		() => ({ articles, columns, setRowHeight }),
		[articles, columns, setRowHeight]
	)

	if (loading) {
		return (
			<div
				className='grid max-md:gap-4 md:gap-6 max-md:py-2 md:py-3 first-of-type:pt-0 last-of-type:pb-0 px-4'
				style={{
					gridTemplateColumns: `repeat(${columns}, minmax(0, 1fr))`
				}}
			>
				{Array.from({ length: 12 }).map((_, index) => (
					<GridLoading key={index} />
				))}
			</div>
		)
	}

	return (
		<div className='h-[calc(100dvh-7rem-2.25rem-1.75rem)] md:h-[calc(100dvh-5rem-2.5rem)] px-4'>
			<List
				className='pb-4'
				listRef={listRef}
				onRowsRendered={onRowsRendered}
				rowComponent={GridRow}
				rowCount={totalRows}
				rowHeight={getRowHeight}
				rowProps={rowProps}
			/>
		</div>
	)
}

export default memo(ArticleGrid)
