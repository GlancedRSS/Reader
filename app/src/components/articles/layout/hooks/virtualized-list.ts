import { useInfiniteLoader } from 'react-window-infinite-loader'

interface UseVirtualizedListOptions {
	isItemLoaded: (index: number) => boolean
	itemCount: number
	loadMoreItems: () => Promise<void>
	threshold: number
}

export function useVirtualizedList({
	isItemLoaded,
	itemCount,
	loadMoreItems,
	threshold
}: UseVirtualizedListOptions) {
	const onRowsRendered = useInfiniteLoader({
		isRowLoaded: isItemLoaded,
		loadMoreRows: async () => {
			await loadMoreItems()
		},
		rowCount: itemCount,
		threshold
	})

	return {
		onRowsRendered
	}
}
