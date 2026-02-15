'use client'

import { Container } from '@/components/articles/layout'
import { useParams } from 'next/navigation'

export default function TagArticlesPage() {
	const params = useParams()
	return (
		<Container
			baseQuery={{ tag_ids: [params.slug as string] }}
			emptyType='all'
		/>
	)
}
