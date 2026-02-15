import {
	useRowHeightCache,
	useVirtualizedList
} from '@/components/articles/layout/hooks'
import { usePathname } from 'next/navigation'
import { memo, useEffect, useMemo, useRef } from 'react'
import { List, RowComponentProps } from 'react-window'

import { ArticleListResponse } from '@/types/api'

const SCROLL_TO_ARTICLE_KEY = 'scroll-to-article-id'
export const SOURCE_LIST_PATH_KEY = 'source-list-path'

interface VirtualizedListProps {
	articles: ArticleListResponse[]
	loading: boolean
	isItemLoaded: (index: number) => boolean
	itemCount: number
	loadMoreItems: () => Promise<void>
	defaultHeight: number
	threshold: number
	rowComponent: React.ComponentType<
		RowComponentProps<{
			articles: ArticleListResponse[]
			setRowHeight: (index: number, height: number) => void
		}>
	>
	containerClassName?: string
	renderLoading: () => React.ReactNode
	extraRowProps?: Record<string, unknown>
}

function VirtualizedList({
	articles,
	loading,
	isItemLoaded,
	itemCount,
	loadMoreItems,
	defaultHeight,
	threshold,
	rowComponent: RowComponent,
	containerClassName,
	renderLoading,
	extraRowProps = {}
}: VirtualizedListProps) {
	const pathname = usePathname()
	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	const listRef = useRef<any>(null)
	const hasScrolledToTarget = useRef(false)

	const { getRowHeight, setRowHeight, clearCacheIfNeeded } = useRowHeightCache({
		defaultHeight
	})

	const { onRowsRendered } = useVirtualizedList({
		isItemLoaded,
		itemCount,
		loadMoreItems,
		threshold
	})

	clearCacheIfNeeded(articles.length)

	useEffect(() => {
		if (hasScrolledToTarget.current || loading || articles.length === 0) {
			return
		}

		const savedArticleId = sessionStorage.getItem(SCROLL_TO_ARTICLE_KEY)
		const sourceListPath = sessionStorage.getItem(SOURCE_LIST_PATH_KEY)

		if (!savedArticleId || sourceListPath !== pathname) {
			if (savedArticleId && sourceListPath !== pathname) {
				sessionStorage.removeItem(SCROLL_TO_ARTICLE_KEY)
				sessionStorage.removeItem(SOURCE_LIST_PATH_KEY)
			}
			return
		}

		const index = articles.findIndex((a) => a?.id === savedArticleId)
		if (index !== -1 && index < articles.length && listRef.current) {
			setTimeout(() => {
				if (listRef.current) {
					listRef.current.scrollToRow({
						align: 'start',
						behavior: 'smooth',
						index
					})
					hasScrolledToTarget.current = true
					sessionStorage.removeItem(SCROLL_TO_ARTICLE_KEY)
					sessionStorage.removeItem(SOURCE_LIST_PATH_KEY)
				}
			}, 100)
		}
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, [loading, articles.length, pathname])

	const rowProps = useMemo(
		() => ({ articles, setRowHeight, ...extraRowProps }),
		[articles, setRowHeight, extraRowProps]
	)

	if (loading) {
		return <>{renderLoading()}</>
	}

	return (
		<div className={containerClassName}>
			<List
				className='pb-4'
				listRef={listRef}
				onRowsRendered={onRowsRendered}
				// eslint-disable-next-line @typescript-eslint/no-explicit-any
				rowComponent={RowComponent as any}
				rowCount={itemCount}
				rowHeight={getRowHeight}
				rowProps={rowProps}
			/>
		</div>
	)
}

export default memo(VirtualizedList)
