'use client'

import { SearchLoading } from '@/components/search/loading'

interface SearchStatusProps {
	className?: string
	isLoading?: boolean
	error?: string | null
	children: React.ReactNode
}

export function SearchStatus({
	className = '',
	isLoading = false,
	error = null,
	children
}: SearchStatusProps) {
	if (isLoading) {
		return (
			<div className={`${className} px-2`}>
				<SearchLoading />
			</div>
		)
	}

	if (error) {
		return (
			<div className={`${className} flex items-center justify-center px-2`}>
				<div className='text-center'>
					<p className='text-destructive'>{error}</p>
				</div>
			</div>
		)
	}

	return <div className={`${className} px-2`}>{children}</div>
}
