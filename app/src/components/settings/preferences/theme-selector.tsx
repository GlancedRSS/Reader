import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue
} from '@/components/ui/select'
import { Skeleton } from '@/components/ui/skeleton'

import { SELECT_WIDTHS, THEME_OPTIONS } from '@/constants/settings'

import type { PreferencesResponse } from '@/types/api'

interface ThemeSelectorProps {
	value: PreferencesResponse['theme']
	onChange: (value: PreferencesResponse['theme']) => void
	disabled?: boolean
}

export function ThemeSelector({
	value,
	onChange,
	disabled = false
}: ThemeSelectorProps) {
	const handleChange = (newTheme: PreferencesResponse['theme']) => {
		onChange(newTheme) // Update local preferences only
	}

	return (
		<div className='flex items-center justify-between'>
			<div>
				<div className='text-sm font-medium'>Theme</div>
				<div className='text-sm text-muted-foreground/80'>
					Light, dark, or system
				</div>
			</div>
			<Select
				disabled={disabled}
				onValueChange={handleChange}
				value={value}
			>
				<SelectTrigger className={`${SELECT_WIDTHS.SHORT} focus:outline-none`}>
					<SelectValue />
				</SelectTrigger>
				<SelectContent>
					{THEME_OPTIONS.map((option) => (
						<SelectItem
							key={option.id}
							value={option.id}
						>
							{option.name}
						</SelectItem>
					))}
				</SelectContent>
			</Select>
		</div>
	)
}

export function ThemeSelectorSkeleton() {
	return (
		<div className='flex items-center justify-between'>
			<div>
				<div className='text-sm font-medium'>Theme</div>
				<div className='text-sm text-muted-foreground/80'>
					Light, dark, or system
				</div>
			</div>
			<Skeleton className={`${SELECT_WIDTHS.SHORT} h-8 rounded-md`} />
		</div>
	)
}
