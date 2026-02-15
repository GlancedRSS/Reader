'use client'

import { ArticleContainer } from '@/components/articles/article'
import { useParams } from 'next/navigation'

export default function ArticlePage() {
	const params = useParams()

	return (
		<div className='h-[calc(100dvh-0.25rem)]'>
			<ArticleContainer id={params.slug as string} />
		</div>
	)
}
