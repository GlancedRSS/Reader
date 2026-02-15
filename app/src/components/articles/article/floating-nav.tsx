'use client'

import { useEffect, useRef, useState } from 'react'
import { IoChevronBack, IoChevronForward } from 'react-icons/io5'

import { Button } from '@/components/ui/button'

import { useIsMobile } from '@/hooks/ui/media-query'

interface FloatingNavProps {
	disabledLeft?: boolean
	disabledRight?: boolean
	onLeft: () => void
	onRight: () => void
}

export function FloatingNav({
	disabledLeft,
	disabledRight,
	onLeft,
	onRight
}: FloatingNavProps) {
	const isMobile = useIsMobile()
	const [isVisible, setIsVisible] = useState(true)
	const timeoutRef = useRef<NodeJS.Timeout | undefined>(undefined)

	useEffect(() => {
		if (!isMobile) return

		const handleScroll = () => {
			setIsVisible(false)

			if (timeoutRef.current) {
				clearTimeout(timeoutRef.current)
			}

			timeoutRef.current = setTimeout(() => {
				setIsVisible(true)
			}, 1000)
		}

		const scrollContainer = document.querySelector(
			'[data-radix-scroll-area-viewport]'
		)
		scrollContainer?.addEventListener('scroll', handleScroll, { passive: true })

		return () => {
			scrollContainer?.removeEventListener('scroll', handleScroll)
			if (timeoutRef.current) {
				clearTimeout(timeoutRef.current)
			}
		}
	}, [isMobile])

	if (!isMobile) return null

	return (
		<>
			{!disabledLeft && (
				<Button
					className='fixed left-0 top-1/2 -translate-y-1/2 z-35 size-10 rounded-l-none! rounded-r-xl shadow-lg transition-opacity'
					onClick={onLeft}
					size='icon'
					style={{ opacity: !isVisible ? 0 : undefined }}
					variant='outline'
				>
					<IoChevronBack className='w-4 h-4' />
					<span className='sr-only'>Previous article</span>
				</Button>
			)}

			{!disabledRight && (
				<Button
					className='fixed right-0 top-1/2 -translate-y-1/2 z-35 size-10 rounded-r-none! rounded-l-xl shadow-lg transition-opacity'
					onClick={onRight}
					size='icon'
					style={{ opacity: !isVisible ? 0 : undefined }}
					variant='outline'
				>
					<IoChevronForward className='w-4 h-4' />
					<span className='sr-only'>Next article</span>
				</Button>
			)}
		</>
	)
}
