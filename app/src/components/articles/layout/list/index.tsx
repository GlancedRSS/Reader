import { VirtualizedList } from '@/components/articles/layout'
import ListArticle from '@/components/articles/layout/list/article'
import ListLoading from '@/components/articles/layout/list/loading'
import { memo } from 'react'

import { useUserPreferences } from '@/hooks/api'

import { ArticleListResponse } from '@/types/api'

function ArticleList({
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

	const getHeight = () => (preferences?.show_summaries ? 81 : 57)

	return (
		<VirtualizedList
			articles={articles}
			containerClassName='h-[calc(100dvh-7rem-2.25rem-1.75rem)] md:h-[calc(100dvh-5rem-2.5rem)]'
			defaultHeight={getHeight()}
			isItemLoaded={isItemLoaded}
			itemCount={itemCount}
			loadMoreItems={loadMoreItems}
			loading={loading}
			renderLoading={() => (
				<div>
					{Array.from({ length: 24 }).map((_, index) => (
						<ListLoading key={index} />
					))}
				</div>
			)}
			rowComponent={ListArticle}
			threshold={6}
		/>
	)
}

export default memo(ArticleList)
