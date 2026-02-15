'use client'

import Sidebar from '@/components/layout/sidebar'

import { useReducedMotion } from '@/hooks/ui/layout'

import { cn } from '@/utils'

type ResponsiveVariant = 'mobile' | 'tablet'

interface ResponsiveSidebarProps {
	isOpen: boolean
	onClose: () => void
	variant: ResponsiveVariant
}

const variantClasses = {
	backdrop: {
		mobile: 'md:hidden',
		tablet: ''
	},
	sidebar: {
		mobile: 'md:hidden touch-manipulation',
		tablet: ''
	}
}

export const ResponsiveSidebar = ({
	isOpen,
	onClose,
	variant
}: ResponsiveSidebarProps) => {
	const prefersReducedMotion = useReducedMotion()

	const animationStyles = prefersReducedMotion
		? {
				contain: 'layout paint',
				transform: isOpen ? 'translate3d(0, 0, 0)' : 'translate3d(-100%, 0, 0)',
				transition: 'none'
			}
		: {
				contain: 'layout paint',
				transform: isOpen ? 'translate3d(0, 0, 0)' : 'translate3d(-100%, 0, 0)',
				transition: 'transform 250ms cubic-bezier(0.25, 0.1, 0.25, 1)',
				willChange: 'transform'
			}

	const backdropAnimationStyles = prefersReducedMotion
		? {
				transition: 'none'
			}
		: {
				contain: 'strict',
				transition: 'opacity 250ms cubic-bezier(0.25, 0.1, 0.25, 1)',
				willChange: 'opacity'
			}

	return (
		<>
			<div
				className={cn(
					'fixed inset-0 bg-black/20 backdrop-blur-sm z-40 transition-opacity',
					variantClasses.backdrop[variant],
					isOpen
						? 'opacity-100 pointer-events-auto'
						: 'opacity-0 pointer-events-none'
				)}
				onClick={onClose}
				style={backdropAnimationStyles}
			/>

			<div
				className={cn(
					'fixed left-0 top-0 bottom-0 bg-sidebar-background border-r border-border/40 flex flex-col z-50',
					variantClasses.sidebar[variant],
					isOpen ? 'pointer-events-auto' : 'pointer-events-none'
				)}
				style={animationStyles}
			>
				<Sidebar />
			</div>
		</>
	)
}
