import {
	forwardRef,
	useCallback,
	useEffect,
	useMemo,
	useRef,
	useState
} from 'react'

import { cn } from '@/utils'

interface AnimatedTabProps {
	items: Array<{
		id: string
		label: string
		icon: React.ComponentType<{ className?: string }>
		icon_active: React.ComponentType<{ className?: string }>
		href: string
	}>
	currentPath?: string
	onItemClick?: (item: AnimatedTabProps['items'][0]) => void
	className?: string
	variant?: 'full' | 'compact'
}

const AnimatedTab = forwardRef<HTMLButtonElement, AnimatedTabProps>(
	({ items, currentPath, onItemClick, className, variant = 'full' }, ref) => {
		const [activeIndex, setActiveIndex] = useState(-1)
		const [buttonHeights, setButtonHeights] = useState<number[]>([])
		const buttonRefs = useRef<(HTMLElement | null)[]>([])
		const resizeObserverRef = useRef<ResizeObserver | null>(null)

		const calculatedActiveIndex = useMemo(() => {
			if (!currentPath) return -1

			return items.findIndex(
				(item) =>
					currentPath === item.href ||
					(currentPath.startsWith(item.href) && item.href !== '/')
			)
		}, [items, currentPath])

		useEffect(() => {
			setActiveIndex(calculatedActiveIndex)
		}, [calculatedActiveIndex])

		useEffect(() => {
			const measureHeights = () => {
				if (!buttonRefs.current) return
				const heights = buttonRefs.current.map((ref) =>
					ref ? ref.offsetHeight : 0
				)
				setButtonHeights(heights)
			}

			if (resizeObserverRef.current) {
				resizeObserverRef.current.disconnect()
			}

			measureHeights()

			resizeObserverRef.current = new ResizeObserver(
				requestAnimationFrame.bind(null, measureHeights)
			)

			buttonRefs.current?.forEach((ref) => {
				if (ref) resizeObserverRef.current?.observe(ref)
			})

			return () => {
				resizeObserverRef.current?.disconnect()
			}
		}, [items.length])

		const handleItemClick = useCallback(
			(item: AnimatedTabProps['items'][0], index: number) => {
				setActiveIndex(index)
				onItemClick?.(item)
			},
			[onItemClick]
		)

		const transformStyle = useMemo(() => {
			if (activeIndex === -1) {
				return { height: '0px', opacity: 0, transform: 'translateY(0px)' }
			}

			let offset = 0
			for (let i = 0; i < activeIndex; i++) {
				offset += buttonHeights[i] || 0
				offset += 8 // 8px gap
			}

			const height = buttonHeights[activeIndex] || 0

			return {
				height: `${height}px`,
				opacity: height > 0 ? 1 : 0,
				transform: `translateY(${offset}px)`
			}
		}, [activeIndex, buttonHeights])

		const showBackground = activeIndex !== -1 && transformStyle.opacity > 0

		return (
			<div
				aria-orientation='vertical'
				className={cn('relative w-full', className)}
				role='tablist'
			>
				{showBackground ? (
					<div
						className='absolute left-0 right-0 bg-accent/80 rounded-lg transition-all duration-250 ease-out z-0'
						style={transformStyle}
					/>
				) : null}

				<div className='relative flex flex-col gap-2'>
					{items.map((item, index) => {
						const isActive = index === activeIndex
						const Icon = isActive ? item.icon_active : item.icon

						return (
							<button
								aria-selected={isActive}
								className={cn(
									'relative rounded-lg flex items-center transition-colors cursor-pointer whitespace-nowrap min-w-0 py-2',
									variant === 'compact'
										? 'justify-center px-2'
										: 'justify-start px-3',
									isActive
										? 'text-accent-foreground font-medium'
										: 'text-muted-foreground dark:text-muted-foreground hover:text-accent-foreground dark:hover:text-accent-foreground'
								)}
								key={item.id}
								onClick={() => handleItemClick(item, index)}
								ref={(el) => {
									if (buttonRefs.current) {
										buttonRefs.current[index] = el
									}
									if (isActive && ref) {
										if (typeof ref === 'function') {
											ref(el)
										} else {
											ref.current = el
										}
									}
								}}
								role='tab'
								type='button'
							>
								{item.icon ? (
									<span
										className={cn(
											'flex items-center',
											variant !== 'compact' && 'mr-3'
										)}
									>
										<Icon className='w-4 h-4 shrink-0' />
									</span>
								) : null}
								{variant !== 'compact' && item.label}
							</button>
						)
					})}
				</div>
			</div>
		)
	}
)

AnimatedTab.displayName = 'AnimatedTab'

export { AnimatedTab }
export type { AnimatedTabProps }
