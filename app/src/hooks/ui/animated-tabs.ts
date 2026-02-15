import { useEffect, useRef, useState } from 'react'

interface UseAnimatedTabOptions {
	activeValue: string
	options: Array<{ id: string }>
	gap?: number
}

export function useAnimatedTabs({
	activeValue,
	options,
	gap = 8
}: UseAnimatedTabOptions) {
	const [buttonWidths, setButtonWidths] = useState<number[]>([])
	const [activeButtonWidth, setActiveButtonWidth] = useState(0)
	const buttonRefs = useRef<(HTMLElement | null)[]>([])

	useEffect(() => {
		const measureWidths = () => {
			const widths = buttonRefs.current.map((ref) =>
				ref ? ref.offsetWidth : 0
			)
			setButtonWidths(widths)

			const activeIndex = options.findIndex(
				(option) => option.id === activeValue
			)
			if (activeIndex !== -1 && widths[activeIndex]) {
				setActiveButtonWidth(widths[activeIndex])
			}
		}

		measureWidths()

		const resizeObserver = new ResizeObserver(measureWidths)
		buttonRefs.current.forEach((ref) => {
			if (ref) resizeObserver.observe(ref)
		})

		return () => {
			resizeObserver.disconnect()
		}
	}, [activeValue, options])

	const calculateTransform = (value: string) => {
		const activeIndex = options.findIndex((option) => option.id === value)
		if (activeIndex === -1 || activeIndex === 0) return '0px'

		let offset = 0
		for (let i = 0; i < activeIndex; i++) {
			offset += buttonWidths[i] || 0
			offset += gap
		}

		return `${offset}px`
	}

	return {
		activeButtonWidth,
		buttonRefs,
		calculateTransform
	}
}
