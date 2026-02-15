import * as AvatarPrimitive from '@radix-ui/react-avatar'
import * as React from 'react'

import { cn } from '@/utils'

interface AvatarProps
	extends React.ComponentProps<typeof AvatarPrimitive.Root> {
	variant?: 'default' | 'sm' | 'lg' | 'xl' | 'mobile' | 'tiny'
}

function Avatar({ className, variant = 'default', ...props }: AvatarProps) {
	const sizeVariants = {
		default: 'size-8 sm:size-6',
		lg: 'size-10 sm:size-8',
		mobile: 'size-10 sm:size-8',
		sm: 'size-6 sm:size-5',
		tiny: 'size-5',
		xl: 'size-12 sm:size-10'
	}

	return (
		<AvatarPrimitive.Root
			className={cn(
				'relative flex shrink-0 overflow-hidden rounded-full',
				sizeVariants[variant],
				className
			)}
			data-slot='avatar'
			{...props}
		/>
	)
}

function AvatarImage({
	className,
	...props
}: React.ComponentProps<typeof AvatarPrimitive.Image>) {
	return (
		<AvatarPrimitive.Image
			className={cn('aspect-square size-full', className)}
			data-slot='avatar-image'
			{...props}
		/>
	)
}

interface AvatarFallbackProps
	extends React.ComponentProps<typeof AvatarPrimitive.Fallback> {
	variant?: 'default' | 'sm' | 'lg' | 'xl' | 'mobile' | 'tiny'
}

function AvatarFallback({
	className,
	variant = 'default',
	...props
}: AvatarFallbackProps) {
	const textSizeVariants = {
		default: 'text-xs sm:text-xs',
		lg: 'text-sm sm:text-sm',
		mobile: 'text-sm sm:text-xs',
		sm: 'text-xs sm:text-xs',
		tiny: 'text-xs',
		xl: 'text-base sm:text-base'
	}

	return (
		<AvatarPrimitive.Fallback
			className={cn(
				'dark:bg-accent text-accent-foreground bg-accent dark:text-accent-foreground flex size-full items-center justify-center rounded-full',
				textSizeVariants[variant],
				className
			)}
			data-slot='avatar-fallback'
			{...props}
		/>
	)
}

export { Avatar, AvatarFallback, AvatarImage }
