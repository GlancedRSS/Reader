import { useCallback, useRef } from 'react'

interface UseRowHeightCacheOptions {
	defaultHeight: number
}

interface RowHeightsCache {
	[key: number]: number
	_prevLength?: number
}

export function useRowHeightCache({ defaultHeight }: UseRowHeightCacheOptions) {
	// Cache for row heights to prevent re-measurement
	const rowHeightsCache = useRef<RowHeightsCache>({})

	// Track if we've seen this index before to prevent re-measurement
	const measuredIndices = useRef<Set<number>>(new Set())

	const getRowHeight = useCallback(
		(index: number) => {
			return rowHeightsCache.current[index] || defaultHeight
		},
		[defaultHeight]
	)

	// Set row height in cache (called by row component after measurement)
	const setRowHeight = useCallback((index: number, height: number) => {
		const isNewMeasurement = !measuredIndices.current.has(index)
		if (isNewMeasurement) {
			rowHeightsCache.current[index] = height
			measuredIndices.current.add(index)

			// Note: In react-window v2, there's no resetAfterIndex method
			// The list will recalculate on next render when rowHeight returns different values
		}
	}, [])

	// Clear cache when articles length decreases (e.g., filter changes)
	const clearCacheIfNeeded = useCallback((articlesLength: number) => {
		const prevLength = rowHeightsCache.current._prevLength ?? articlesLength

		if (articlesLength < prevLength) {
			rowHeightsCache.current = {}
			measuredIndices.current.clear()
		}

		rowHeightsCache.current._prevLength = articlesLength
	}, [])

	return {
		clearCacheIfNeeded,
		getRowHeight,
		setRowHeight
	}
}
