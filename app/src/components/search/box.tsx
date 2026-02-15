'use client'

import { Input } from '@/components/ui/input'

interface SearchBoxProps {
	className?: string
	placeholder?: string
	value: string
	onChange: (value: string) => void
	autoFocus?: boolean
}

export function SearchBox({
	className,
	placeholder,
	value,
	onChange,
	autoFocus = false
}: SearchBoxProps) {
	return (
		<div
			className={`${className} sticky top-0 z-10 bg-background px-4 pb-0.5 xl:max-w-[992px]`}
		>
			<Input
				autoFocus={autoFocus}
				onChange={(e) => onChange(e.target.value)}
				placeholder={placeholder}
				value={value}
			/>
		</div>
	)
}
