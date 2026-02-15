import { ReactNode } from 'react'

import { Button } from '@/components/ui/button'

import { cn } from '@/utils'

interface NavigationOption {
	id: string
	label: string
	icon: ReactNode
	description?: string
	disabled?: boolean
}

interface NavigationProps {
	options: NavigationOption[]
	onChange?: (tabId: string) => void
	className?: string
}

export function Navigation({ options, onChange, className }: NavigationProps) {
	const handleButtonClick = (tabId: string) => {
		const option = options.find((opt) => opt.id === tabId)
		if (option && !option.disabled) {
			onChange?.(tabId)
		}
	}

	return (
		<div
			className={cn(
				'fixed bottom-0 left-0 right-0 bg-sidebar-background border-t border-border z-30',
				className
			)}
		>
			<div className='flex items-center justify-around min-h-14 h-14 p-1 gap-1'>
				{options.map((tab) => (
					<Button
						aria-disabled={tab.disabled}
						className={cn(
							'relative z-10 flex flex-col items-center gap-1 px-2 py-1 rounded-lg min-w-0 flex-1 w-full min-h-11',
							'text-muted-foreground/80 dark:text-muted-foreground/80 hover:text-accent-foreground dark:hover:text-accent-foreground',
							tab.disabled && 'cursor-not-allowed opacity-50'
						)}
						disabled={tab.disabled}
						key={tab.id}
						onClick={() => handleButtonClick(tab.id)}
						title={tab.description}
						variant='ghost'
					>
						<span className={tab.id.includes('#') ? 'scale-150' : 'scale-125'}>
							{tab.icon}
						</span>
						<span className='text-xs -mb-1.5 mt-0.5 font-medium truncate max-w-full'>
							{tab.label}
						</span>
					</Button>
				))}
			</div>
		</div>
	)
}

interface NavigationWrapperProps {
	children: ReactNode
	className?: string
}

export function NavigationWrapper({
	children,
	className
}: NavigationWrapperProps) {
	return <div className={cn('pb-16', className)}>{children}</div>
}
