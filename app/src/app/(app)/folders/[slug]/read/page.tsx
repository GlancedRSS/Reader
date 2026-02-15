'use client'

import { Container } from '@/components/articles/layout'
import { useParams } from 'next/navigation'

export default function ReadArticlesPage() {
	const params = useParams()
	return (
		<Container
			baseQuery={{
				folder_ids: [params.slug as string],
				is_read: 'read'
			}}
			emptyType='read'
		/>
	)
}
