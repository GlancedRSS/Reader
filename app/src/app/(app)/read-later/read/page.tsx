'use client'

import { Container } from '@/components/articles/layout'

export default function ReadArticlesPage() {
	return (
		<Container
			baseQuery={{ is_read: 'read', read_later: 'true' }}
			emptyType='read-later-read'
		/>
	)
}
