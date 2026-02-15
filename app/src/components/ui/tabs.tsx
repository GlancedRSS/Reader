'use client'

import { ReactNode, useCallback, useEffect, useState } from 'react'

import { useAnimatedTabs } from '@/hooks/ui/animated-tabs'

import type { TabSection } from '@/types/layout'

import { cn } from '@/utils'

interface TabOption {
	id: string
	label?: string
	icon?: ReactNode
	description?: string
	disabled?: boolean
	badge?: string | number
	render?: (props: { isActive: boolean; onClick: () => void }) => ReactNode
}

interface TabsProps {
	options: TabOption[]
	value: string
	onChange?: (tabId: string) => void
	gap?: number
	backgroundWidth?: number
	variant?: 'default' | 'compact' | 'large' | 'icon'
	className?: string
	backgroundClassName?: string
	tabClassName?: string
	animateContent?: boolean
	tabSections?: TabSection[]
	currentPath?: string
	onAnimationChange?: (animationState: {
		animationClass: string
		key: number
	}) => void
}

const variants = {
	compact: {
		background: 'top-1 bottom-1 left-1 rounded-lg',
		container: 'gap-0.5 p-1',
		tab: 'h-6 px-2 text-sm font-medium sm:h-5 sm:px-1.5 sm:text-xs'
	},
	default: {
		background: 'top-1 bottom-1 left-1 rounded-lg',
		container: 'gap-0.5 p-1',
		tab: 'h-7 px-3 text-base font-semibold sm:h-7 sm:px-2 sm:text-xs sm:font-medium'
	},
	icon: {
		background: 'top-1 bottom-1 left-1 rounded-lg',
		container: 'gap-0.5 p-1',
		tab: 'h-10 w-10 sm:h-7 sm:w-7'
	},
	large: {
		background: 'top-1 bottom-1 left-1 rounded-lg',
		container: 'gap-0.5 p-1',
		tab: 'h-8 px-4 text-lg font-semibold sm:h-8 sm:px-3 sm:text-sm'
	}
}

export function Tabs({
	options,
	value,
	onChange,
	gap = 2,
	backgroundWidth,
	variant = 'default',
	className,
	backgroundClassName,
	tabClassName,
	animateContent = false,
	tabSections,
	currentPath,
	onAnimationChange
}: TabsProps) {
	const { buttonRefs, activeButtonWidth, calculateTransform } = useAnimatedTabs(
		{
			activeValue: value,
			gap,
			options
		}
	)

	const sizeConfig = variants[variant]

	const [animationState, setAnimationState] = useState({
		animationClass: '',
		key: 0,
		prevIndex: -1
	})

	const getCurrentPathIndex = useCallback(() => {
		if (!tabSections || !currentPath) return 0
		const currentIndex = tabSections.findIndex(
			(tab) => tab.route === currentPath
		)
		return currentIndex >= 0 ? currentIndex : 0
	}, [tabSections, currentPath])

	const getCurrentOptionIndex = useCallback(() => {
		const currentIndex = options.findIndex((option) => option.id === value)
		return currentIndex >= 0 ? currentIndex : 0
	}, [options, value])

	useEffect(() => {
		if (!animateContent) return

		const currentIndex = tabSections
			? getCurrentPathIndex()
			: getCurrentOptionIndex()

		if (
			animationState.prevIndex !== -1 &&
			animationState.prevIndex !== currentIndex
		) {
			const direction =
				currentIndex > animationState.prevIndex ? 'right' : 'left'

			const newAnimationState = {
				animationClass: `tab-slide-${direction}`,
				key: animationState.key + 1,
				prevIndex: currentIndex
			}

			setAnimationState(newAnimationState)

			onAnimationChange?.({
				animationClass: newAnimationState.animationClass,
				key: newAnimationState.key
			})
		} else if (animationState.prevIndex === -1) {
			setAnimationState((prev) => ({ ...prev, prevIndex: currentIndex }))
		}
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, [
		value,
		currentPath,
		animateContent,
		tabSections,
		getCurrentPathIndex,
		getCurrentOptionIndex,
		onAnimationChange
	])

	const handleTabClick = (tabId: string) => {
		const option = options.find((opt) => opt.id === tabId)
		if (option && !option.disabled) {
			onChange?.(tabId)
		}
	}

	const tabsContent = (
		<div className={cn('relative flex', sizeConfig.container)}>
			{options.map((option, index) => {
				const isActive = option.id === value
				const isDisabled = option.disabled

				if (option.render) {
					return (
						<div
							aria-disabled={isDisabled}
							aria-selected={isActive}
							className={cn(
								'relative rounded flex items-center justify-center',
								sizeConfig.tab,
								tabClassName
							)}
							key={option.id}
							ref={(el) => {
								buttonRefs.current[index] = el
							}}
							role='tab'
						>
							{option.render({
								isActive,
								onClick: () => handleTabClick(option.id)
							})}
						</div>
					)
				}

				return (
					<button
						aria-disabled={isDisabled}
						aria-label={
							option.description || `${option.label || option.id} tab`
						}
						aria-selected={isActive}
						className={cn(
							'relative rounded flex items-center justify-center transition-colors cursor-pointer whitespace-nowrap min-w-0',
							sizeConfig.tab,
							isActive
								? 'text-accent-foreground'
								: isDisabled
									? 'text-muted-foreground/60 cursor-not-allowed opacity-50'
									: 'text-muted-foreground/60 dark:text-muted-foreground/80 hover:text-accent-foreground dark:hover:text-accent-foreground',
							tabClassName
						)}
						disabled={isDisabled}
						key={option.id}
						onClick={() => handleTabClick(option.id)}
						ref={(el) => {
							buttonRefs.current[index] = el
						}}
						role='tab'
						type='button'
					>
						{option.icon ? (
							<span className={cn('flex items-center', option.label && 'mr-2')}>
								{option.icon}
							</span>
						) : null}
						{option.label}
						{option.badge ? (
							<span
								className={cn(
									'ml-2 min-w-[20px] h-5 rounded-full text-sm font-medium flex items-center justify-center px-1.5 sm:min-w-[16px] sm:h-4 sm:text-xs sm:px-1',
									isActive
										? 'bg-primary text-primary-foreground'
										: 'bg-destructive text-destructive-foreground'
								)}
							>
								{option.badge}
							</span>
						) : null}
					</button>
				)
			})}
		</div>
	)

	return (
		<div className={cn('relative rounded-md', className)}>
			<div
				className={cn(
					'absolute bg-accent/80 transition-all duration-200 ease-out',
					sizeConfig.background,
					backgroundClassName
				)}
				style={{
					transform: `translateX(${calculateTransform(value)})`,
					width: `${backgroundWidth || activeButtonWidth}px`
				}}
			/>
			{tabsContent}
		</div>
	)
}
