'use client'

import { Container } from '@/components/articles/layout'
import { useParams } from 'next/navigation'

export default function UnreadArticlesPage() {
	const params = useParams()
	return (
		<Container
			baseQuery={{ is_read: 'unread', tag_ids: [params.slug as string] }}
			emptyType='unread'
		/>
	)
}
