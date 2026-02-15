import { cn } from '@/utils'

interface LoaderProps {
	className?: string
	size?: 'sm' | 'md' | 'lg'
}

export function Loader({ className, size = 'sm' }: LoaderProps) {
	const sizeClasses = {
		lg: 'w-8 h-8 border-2',
		md: 'w-6 h-6 border-2',
		sm: 'w-4 h-4 border-2'
	}

	return (
		<div
			className={cn(
				'border-current border-t-transparent rounded-full animate-spin',
				sizeClasses[size],
				className
			)}
		/>
	)
}
