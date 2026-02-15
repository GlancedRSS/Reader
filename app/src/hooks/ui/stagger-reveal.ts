import gsap from 'gsap'
import { useEffect } from 'react'

export type StaggerRevealConfig = {
	initialOpacity?: number
	initialY?: number
	duration?: number
	stagger?: number
	delay?: number
	ease?: string
}

export function useStaggerReveal(
	containerRef: React.RefObject<HTMLElement | null>,
	contentRef: React.RefObject<HTMLElement | null>,
	config: StaggerRevealConfig = {}
) {
	const {
		initialOpacity = 0,
		initialY = 30,
		duration = 0.6,
		stagger = 0.15,
		delay = 0.3,
		ease = 'power2.out'
	} = config

	useEffect(() => {
		const container = containerRef.current
		const content = contentRef.current

		if (!container || !content) return

		const ctx = gsap.context(() => {
			gsap.fromTo(
				content.children,
				{ opacity: initialOpacity, y: initialY },
				{ delay, duration, ease, opacity: 1, stagger, y: 0 }
			)

			gsap.fromTo(
				container,
				{ opacity: initialOpacity },
				{ duration: 0.4, ease: 'power2.out', opacity: 1 }
			)
		}, container)

		return () => ctx.revert()
	}, [
		containerRef,
		contentRef,
		initialOpacity,
		initialY,
		duration,
		stagger,
		delay,
		ease
	])
}
