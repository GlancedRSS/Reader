import { VirtualizedList } from '@/components/articles/layout'
import MagazineArticle from '@/components/articles/layout/magazine/article'
import MagazineLoading from '@/components/articles/layout/magazine/loading'
import { memo, useEffect, useMemo, useState } from 'react'

import { useUserPreferences } from '@/hooks/api'

import { ArticleListResponse } from '@/types/api'

function Magazine({
	articles,
	loading,
	isItemLoaded,
	itemCount,
	loadMoreItems
}: {
	articles: ArticleListResponse[]
	loading: boolean
	isItemLoaded: (index: number) => boolean
	itemCount: number
	loadMoreItems: () => Promise<void>
}) {
	const { data: preferences } = useUserPreferences()
	const [windowWidth, setWindowWidth] = useState(0)

	useEffect(() => {
		const handleResize = () => setWindowWidth(window.innerWidth)
		handleResize()
		window.addEventListener('resize', handleResize)
		return () => window.removeEventListener('resize', handleResize)
	}, [])

	const defaultHeight = useMemo(() => {
		if (windowWidth < 1024) {
			if (windowWidth < 640) {
				return preferences?.show_summaries ? 144 : 88
			} else if (windowWidth >= 640 && windowWidth < 768) {
				if (preferences?.show_article_thumbnails) {
					return 112
				}
				if (preferences?.show_summaries) {
					return 120
				}
				return 88
			} else {
				if (preferences?.show_article_thumbnails) {
					return 144
				}
				if (preferences?.show_summaries) {
					return 112
				}
				return 88
			}
		}
		return preferences?.show_summaries ? 144 : 88
	}, [
		windowWidth,
		preferences?.show_article_thumbnails,
		preferences?.show_summaries
	])

	return (
		<VirtualizedList
			articles={articles}
			containerClassName='h-[calc(100dvh-7rem-2.25rem-1.75rem)] md:h-[calc(100dvh-5rem-2.5rem)] px-2'
			defaultHeight={defaultHeight}
			isItemLoaded={isItemLoaded}
			itemCount={itemCount}
			loadMoreItems={loadMoreItems}
			loading={loading}
			renderLoading={() => (
				<div className='px-4 py-2 space-y-4'>
					{Array.from({ length: 12 }).map((_, loadingIndex) => (
						<MagazineLoading key={loadingIndex} />
					))}
				</div>
			)}
			rowComponent={MagazineArticle}
			threshold={4}
		/>
	)
}

export default memo(Magazine)
