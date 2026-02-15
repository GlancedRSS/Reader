'use client'

import { Container } from '@/components/articles/layout'

export default function UnreadArticlesPage() {
	return (
		<Container
			baseQuery={{ is_read: 'unread', read_later: 'true' }}
			emptyType='read-later-unread'
		/>
	)
}
