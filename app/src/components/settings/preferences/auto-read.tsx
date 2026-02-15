import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue
} from '@/components/ui/select'
import { Skeleton } from '@/components/ui/skeleton'

import { AUTO_READ_OPTIONS, SELECT_WIDTHS } from '@/constants/settings'

import type { PreferencesResponse } from '@/types/api'

interface AutoReadProps {
	value: PreferencesResponse['auto_mark_as_read']
	onChange: (value: PreferencesResponse['auto_mark_as_read']) => void
	disabled?: boolean
}

export function AutoRead({ value, onChange, disabled = false }: AutoReadProps) {
	return (
		<div className='flex items-center justify-between'>
			<div>
				<div className='text-sm font-medium'>Mark as Read</div>
				<div className='text-sm text-muted-foreground/80'>
					Auto-read older articles
				</div>
			</div>
			<Select
				disabled={disabled}
				onValueChange={(value: PreferencesResponse['auto_mark_as_read']) =>
					onChange(value)
				}
				value={value.toString()}
			>
				<SelectTrigger className={SELECT_WIDTHS.SHORT}>
					<SelectValue />
				</SelectTrigger>
				<SelectContent>
					{AUTO_READ_OPTIONS.map((option) => (
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

export function AutoReadSkeleton() {
	return (
		<div className='flex items-center justify-between'>
			<div>
				<div className='text-sm font-medium'>Mark as Read</div>
				<div className='text-sm text-muted-foreground/80'>
					Auto-read older articles
				</div>
			</div>
			<Skeleton className={`${SELECT_WIDTHS.SHORT} h-8 rounded-md`} />
		</div>
	)
}
