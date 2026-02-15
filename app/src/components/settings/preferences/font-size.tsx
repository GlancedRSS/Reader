import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue
} from '@/components/ui/select'
import { Skeleton } from '@/components/ui/skeleton'

import { FONT_SIZE_OPTIONS, SELECT_WIDTHS } from '@/constants/settings'

import type { PreferencesResponse } from '@/types/api'

interface FontSizeProps {
	value: PreferencesResponse['font_size']
	onChange: (value: PreferencesResponse['font_size']) => void
	disabled?: boolean
}

export function FontSize({ value, onChange, disabled = false }: FontSizeProps) {
	return (
		<div className='flex items-center justify-between'>
			<div>
				<div className='text-sm font-medium'>Text Size</div>
				<div className='text-sm text-muted-foreground/80'>
					Adjust for readability
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
					{FONT_SIZE_OPTIONS.map((option) => (
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

export function FontSizeSkeleton() {
	return (
		<div className='flex items-center justify-between'>
			<div>
				<div className='text-sm font-medium'>Text Size</div>
				<div className='text-sm text-muted-foreground/80'>
					Adjust for readability
				</div>
			</div>
			<Skeleton className={`${SELECT_WIDTHS.SHORT} h-8 rounded-md`} />
		</div>
	)
}
