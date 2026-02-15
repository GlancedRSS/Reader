import { cn } from '@/utils'

function Skeleton({ className, ...props }: React.ComponentProps<'div'>) {
	return (
		<div
			className={cn(
				'bg-neutral-200 dark:bg-neutral-800 animate-pulse rounded-md',
				className
			)}
			data-slot='skeleton'
			{...props}
		/>
	)
}

export { Skeleton }
