'use client'

import { Container } from '@/components/articles/layout'

export default function UnreadArticlesPage() {
	return (
		<Container
			baseQuery={{ is_read: 'unread' }}
			emptyType='unread'
		/>
	)
}
