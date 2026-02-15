'use client'

interface SearchEmptyProps {
	message?: string
}

export function SearchEmpty({ message }: SearchEmptyProps) {
	return (
		<div className='flex items-center justify-center py-8'>
			<div className='text-center'>
				<p className='text-muted-foreground'>
					{message || 'No results found. Try different keywords.'}
				</p>
			</div>
		</div>
	)
}
