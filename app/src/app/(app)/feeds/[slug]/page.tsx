'use client'

import { Container } from '@/components/articles/layout'
import { useParams } from 'next/navigation'

export default function FeedArticlesPage() {
	const params = useParams()
	return (
		<Container
			baseQuery={{ subscription_ids: [params.slug as string] }}
			emptyType='all'
		/>
	)
}
