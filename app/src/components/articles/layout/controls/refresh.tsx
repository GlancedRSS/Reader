'use client'

import { useArticlesPaginationStore } from '@/stores/articles-pagination'
import { IoRefresh } from 'react-icons/io5'
import { useSWRConfig } from 'swr'

import { Button } from '@/components/ui/button'

export function Refresh() {
	const { mutate: swrMutate } = useSWRConfig()
	const { refreshArticles } = useArticlesPaginationStore()

	const handleRefresh = () => {
		refreshArticles()
		swrMutate('/folders/tree')
		swrMutate((key) => typeof key === 'string' && key.startsWith('/articles'))
	}

	return (
		<Button
			aria-label='Refresh'
			onClick={handleRefresh}
			size='sm'
			variant='ghost'
		>
			<IoRefresh className='h-4 w-4' />
		</Button>
	)
}
