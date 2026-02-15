'use client'

import { IoMenu } from 'react-icons/io5'

import { useSidebarToggle } from '@/hooks/ui/layout'

import { cn } from '@/utils'

interface SidebarToggleButtonProps {
	className?: string
	variant?: 'header' | 'inline' | 'floating'
	size?: 'sm' | 'md' | 'lg'
	children?: React.ReactNode
}

export function SidebarToggleButton({
	className,
	variant = 'inline',
	size = 'md',
	children
}: SidebarToggleButtonProps) {
	const { toggleSidebar, isSidebarOpen } = useSidebarToggle()

	const sizeClasses = {
		lg: 'p-3',
		md: 'p-2',
		sm: 'p-1.5'
	}

	const iconSizes = {
		lg: 'w-6 h-6',
		md: 'w-5 h-5',
		sm: 'w-4 h-4'
	}

	const variantClasses = {
		floating:
			'fixed top-4 left-4 z-50 bg-background border border-border/40 shadow-lg rounded-full',
		header:
			'border border-border/40 bg-background/95 backdrop-blur-sm shadow-sm',
		inline: 'hover:bg-muted transition-colors'
	}

	return (
		<button
			aria-expanded={isSidebarOpen}
			aria-label={isSidebarOpen ? 'Close sidebar' : 'Open sidebar'}
			className={cn(
				'rounded-lg touch-manipulation',
				'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
				sizeClasses[size],
				variantClasses[variant],
				isSidebarOpen && 'bg-muted',
				className
			)}
			onClick={toggleSidebar}
		>
			{children || <IoMenu className={iconSizes[size]} />}
		</button>
	)
}
