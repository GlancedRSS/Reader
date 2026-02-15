import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue
} from '@/components/ui/select'
import { Skeleton } from '@/components/ui/skeleton'

import { DATE_FORMAT_OPTIONS, SELECT_WIDTHS } from '@/constants/settings'

import type { PreferencesResponse } from '@/types/api'

interface DateFormatSelectorProps {
	value: PreferencesResponse['date_format']
	onChange: (value: PreferencesResponse['date_format']) => void
	disabled?: boolean
}

export function DateFormatSelector({
	value,
	onChange,
	disabled = false
}: DateFormatSelectorProps) {
	return (
		<div className='flex items-center justify-between'>
			<div>
				<div className='text-sm font-medium'>Date Format</div>
				<div className='text-sm text-muted-foreground/80'>
					Display style for dates
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
					{DATE_FORMAT_OPTIONS.map((option) => (
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

export function DateFormatSelectorSkeleton() {
	return (
		<div className='flex items-center justify-between'>
			<div>
				<div className='text-sm font-medium'>Date Format</div>
				<div className='text-sm text-muted-foreground/80'>
					Display style for dates
				</div>
			</div>
			<Skeleton className={`${SELECT_WIDTHS.SHORT} h-8 rounded-md`} />
		</div>
	)
}
