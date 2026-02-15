import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue
} from '@/components/ui/select'
import { Skeleton } from '@/components/ui/skeleton'

import { ARTICLE_LAYOUT_OPTIONS, SELECT_WIDTHS } from '@/constants/settings'

import type { PreferencesResponse } from '@/types/api'

interface ArticleLayoutProps {
	value: PreferencesResponse['article_layout']
	onChange: (value: PreferencesResponse['article_layout']) => void
	disabled?: boolean
}

export function ArticleLayout({
	value,
	onChange,
	disabled = false
}: ArticleLayoutProps) {
	return (
		<div className='flex items-center justify-between'>
			<div>
				<div className='text-sm font-medium'>Article View</div>
				<div className='text-sm text-muted-foreground/80'>
					How articles are displayed
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
					{ARTICLE_LAYOUT_OPTIONS.map((option) => (
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

export function ArticleLayoutSkeleton() {
	return (
		<div className='flex items-center justify-between'>
			<div>
				<div className='text-sm font-medium'>Article View</div>
				<div className='text-sm text-muted-foreground/80'>
					How articles are displayed
				</div>
			</div>
			<Skeleton className={`${SELECT_WIDTHS.SHORT} h-8 rounded-md`} />
		</div>
	)
}
