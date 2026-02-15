'use client'

import { Container } from '@/components/articles/layout'
import { useParams } from 'next/navigation'

export default function ReadArticlesPage() {
	const params = useParams()
	return (
		<Container
			baseQuery={{
				is_read: 'read',
				subscription_ids: [params.slug as string]
			}}
			emptyType='read'
		/>
	)
}
