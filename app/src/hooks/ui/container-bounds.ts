'use client'

import { useEffect, useState } from 'react'

interface ContainerBounds {
	left: number
	width: number
}

export function useContainerBounds(
	containerRef: React.RefObject<HTMLElement | null>
) {
	const [bounds, setBounds] = useState<ContainerBounds>({ left: 0, width: 0 })

	useEffect(() => {
		const container = containerRef.current
		if (!container) return

		const updateBounds = () => {
			const rect = container.getBoundingClientRect()
			setBounds((prev) => {
				if (prev.left === rect.left && prev.width === rect.width) {
					return prev
				}
				return {
					left: rect.left,
					width: rect.width
				}
			})
		}

		updateBounds()

		const resizeObserver = new ResizeObserver(updateBounds)
		resizeObserver.observe(container)

		window.addEventListener('resize', updateBounds)

		return () => {
			resizeObserver.disconnect()
			window.removeEventListener('resize', updateBounds)
		}
	}, [containerRef])

	return bounds
}
