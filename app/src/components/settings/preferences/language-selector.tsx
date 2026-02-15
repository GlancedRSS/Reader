import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue
} from '@/components/ui/select'
import { Skeleton } from '@/components/ui/skeleton'

import { LANGUAGES, SELECT_WIDTHS } from '@/constants/settings'

import type { PreferencesResponse } from '@/types/api'

interface LanguageSelectorProps {
	value: PreferencesResponse['language']
	onChange: (value: PreferencesResponse['language']) => void
	disabled?: boolean
}

export function LanguageSelector({
	value,
	onChange,
	disabled = false
}: LanguageSelectorProps) {
	return (
		<div className='flex items-center justify-between'>
			<div>
				<div className='text-sm font-medium'>Language</div>
				<div className='text-sm text-muted-foreground/80'>
					Interface language
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
					{LANGUAGES.map((lang) => (
						<SelectItem
							key={lang.code}
							value={lang.code}
						>
							{lang.name}
						</SelectItem>
					))}
				</SelectContent>
			</Select>
		</div>
	)
}

export function LanguageSelectorSkeleton() {
	return (
		<div className='flex items-center justify-between'>
			<div>
				<div className='text-sm font-medium'>Language</div>
				<div className='text-sm text-muted-foreground/80'>
					Interface language
				</div>
			</div>
			<Skeleton className={`${SELECT_WIDTHS.SHORT} h-8 rounded-md`} />
		</div>
	)
}
