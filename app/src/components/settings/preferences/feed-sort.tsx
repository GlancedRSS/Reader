import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue
} from '@/components/ui/select'
import { Skeleton } from '@/components/ui/skeleton'

import { FEED_SORT_ORDER_OPTIONS, SELECT_WIDTHS } from '@/constants/settings'

import type { PreferencesResponse } from '@/types/api'

interface FeedSortProps {
	value: PreferencesResponse['feed_sort_order']
	onChange: (value: PreferencesResponse['feed_sort_order']) => void
	disabled?: boolean
}

export function FeedSort({ value, onChange, disabled = false }: FeedSortProps) {
	return (
		<div className='flex items-center justify-between'>
			<div>
				<div className='text-sm font-medium'>Sort By</div>
				<div className='text-sm text-muted-foreground/80'>
					Default feed order
				</div>
			</div>
			<Select
				disabled={disabled}
				onValueChange={onChange}
				value={value}
			>
				<SelectTrigger className={SELECT_WIDTHS.SHORT}>
					<SelectValue />
				</SelectTrigger>
				<SelectContent>
					{FEED_SORT_ORDER_OPTIONS.map((option) => (
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

export function FeedSortSkeleton() {
	return (
		<div className='flex items-center justify-between'>
			<div>
				<div className='text-sm font-medium'>Sort By</div>
				<div className='text-sm text-muted-foreground/80'>
					Default feed order
				</div>
			</div>
			<Skeleton className={`${SELECT_WIDTHS.SHORT} h-8 rounded-md`} />
		</div>
	)
}
