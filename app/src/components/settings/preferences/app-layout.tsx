import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue
} from '@/components/ui/select'
import { Skeleton } from '@/components/ui/skeleton'

import { APP_LAYOUT_OPTIONS, SELECT_WIDTHS } from '@/constants/settings'

import type { PreferencesResponse } from '@/types/api'

interface AppLayoutProps {
	value: PreferencesResponse['app_layout']
	onChange: (value: PreferencesResponse['app_layout']) => void
	disabled?: boolean
}

export function AppLayout({
	value,
	onChange,
	disabled = false
}: AppLayoutProps) {
	return (
		<div className='flex items-center justify-between'>
			<div>
				<div className='text-sm font-medium'>Layout</div>
				<div className='text-sm text-muted-foreground/80'>
					Sidebar and feed arrangement
				</div>
			</div>
			<Select
				disabled={disabled}
				onValueChange={(value: PreferencesResponse['app_layout']) =>
					onChange(value)
				}
				value={value.toString()}
			>
				<SelectTrigger className={SELECT_WIDTHS.SHORT}>
					<SelectValue />
				</SelectTrigger>
				<SelectContent>
					{APP_LAYOUT_OPTIONS.map((option) => (
						<SelectItem
							key={option.value}
							value={option.value.toString()}
						>
							{option.label}
						</SelectItem>
					))}
				</SelectContent>
			</Select>
		</div>
	)
}

export function AppLayoutSkeleton() {
	return (
		<div className='flex items-center justify-between'>
			<div>
				<div className='text-sm font-medium'>Layout</div>
				<div className='text-sm text-muted-foreground/80'>
					Sidebar and feed arrangement
				</div>
			</div>
			<Skeleton className={`${SELECT_WIDTHS.SHORT} h-8 rounded-md`} />
		</div>
	)
}
