import GridArticle from '@/components/articles/layout/grid/article'
import GridLoading from '@/components/articles/layout/grid/loading'
import { useEffect, useRef } from 'react'
import { RowComponentProps } from 'react-window'

import { ArticleListResponse } from '@/types/api'

export function GridRow({
	index,
	articles,
	columns,
	style,
	setRowHeight
}: RowComponentProps<{
	articles: ArticleListResponse[]
	columns: number
	setRowHeight: (index: number, height: number) => void
}>) {
	const rowRef = useRef<HTMLDivElement>(null)
	const hasMeasuredColumns = useRef<Set<number>>(new Set())

	useEffect(() => {
		if (rowRef.current && !hasMeasuredColumns.current.has(columns)) {
			requestAnimationFrame(() => {
				if (rowRef.current) {
					const height = rowRef.current.offsetHeight
					setRowHeight(index, height)
					hasMeasuredColumns.current.add(columns)
				}
			})
		}
	}, [index, columns, setRowHeight])

	const startIndex = index * columns
	const endIndex = startIndex + columns
	const rowArticles = articles.slice(startIndex, endIndex)

	const isLoadingRow = rowArticles.some((article) => !article)

	return (
		<div
			className='grid max-md:gap-4 md:gap-6 max-md:py-2 md:py-3 first-of-type:pt-0 last-of-type:pb-0'
			ref={rowRef}
			style={{
				...style,
				gridTemplateColumns: `repeat(${columns}, minmax(0, 1fr))`
			}}
		>
			{isLoadingRow
				? Array.from({ length: 12 }).map((_, loadingIndex) => (
						<GridLoading key={`loading-${loadingIndex}`} />
					))
				: rowArticles.map((article) => (
						<GridArticle
							article={article}
							key={article.id}
						/>
					))}
		</div>
	)
}
