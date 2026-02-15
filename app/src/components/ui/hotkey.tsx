import { cn } from '@/utils'

interface HotkeyProps {
	children: React.ReactNode
	className?: string
}

export function Hotkey({ children, className }: HotkeyProps) {
	return (
		<div
			className={cn(
				'bg-sidebar-background border px-1.5 py-0.5 rounded-lg text-xs font-medium',
				className
			)}
		>
			{children}
		</div>
	)
}
