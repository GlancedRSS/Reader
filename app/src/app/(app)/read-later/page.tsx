'use client'

import { Container } from '@/components/articles/layout'

export default function AllArticlesPage() {
	return (
		<Container
			baseQuery={{ read_later: 'true' }}
			emptyType='read-later'
		/>
	)
}
