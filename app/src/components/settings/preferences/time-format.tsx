import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue
} from '@/components/ui/select'
import { Skeleton } from '@/components/ui/skeleton'

import { SELECT_WIDTHS, TIME_FORMAT_OPTIONS } from '@/constants/settings'

import type { PreferencesResponse } from '@/types/api'

interface TimeFormatSelectorProps {
	value: PreferencesResponse['time_format']
	onChange: (value: PreferencesResponse['time_format']) => void
	disabled?: boolean
}

export function TimeFormatSelector({
	value,
	onChange,
	disabled = false
}: TimeFormatSelectorProps) {
	return (
		<div className='flex items-center justify-between'>
			<div>
				<div className='text-sm font-medium'>Time Format</div>
				<div className='text-sm text-muted-foreground/80'>
					12-hour or 24-hour clock
				</div>
			</div>
			<Select
				disabled={disabled}
				onValueChange={onChange}
				value={value}
			>
				<SelectTrigger className={`${SELECT_WIDTHS.SHORT} focus:outline-none`}>
					<SelectValue />
				</SelectTrigger>
				<SelectContent>
					{TIME_FORMAT_OPTIONS.map((option) => (
						<SelectItem
							key={option.value}
							value={option.value}
						>
							{option.label}
						</SelectItem>
					))}
				</SelectContent>
			</Select>
		</div>
	)
}

export function TimeFormatSelectorSkeleton() {
	return (
		<div className='flex items-center justify-between'>
			<div>
				<div className='text-sm font-medium'>Time Format</div>
				<div className='text-sm text-muted-foreground/80'>
					12-hour or 24-hour clock
				</div>
			</div>
			<Skeleton className={`${SELECT_WIDTHS.SHORT} h-8 rounded-md`} />
		</div>
	)
}
