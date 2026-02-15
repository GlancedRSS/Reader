import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue
} from '@/components/ui/select'
import { Skeleton } from '@/components/ui/skeleton'

import { FONT_SPACING_OPTIONS, SELECT_WIDTHS } from '@/constants/settings'

import type { PreferencesResponse } from '@/types/api'

interface FontSpacingProps {
	value: PreferencesResponse['font_spacing']
	onChange: (value: PreferencesResponse['font_spacing']) => void
	disabled?: boolean
}

export function FontSpacing({
	value,
	onChange,
	disabled = false
}: FontSpacingProps) {
	return (
		<div className='flex items-center justify-between'>
			<div>
				<div className='text-sm font-medium'>Line Height</div>
				<div className='text-sm text-muted-foreground/80'>
					Space between lines
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
					{FONT_SPACING_OPTIONS.map((option) => (
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

export function FontSpacingSkeleton() {
	return (
		<div className='flex items-center justify-between'>
			<div>
				<div className='text-sm font-medium'>Line Height</div>
				<div className='text-sm text-muted-foreground/80'>
					Space between lines
				</div>
			</div>
			<Skeleton className={`${SELECT_WIDTHS.SHORT} h-8 rounded-md`} />
		</div>
	)
}
