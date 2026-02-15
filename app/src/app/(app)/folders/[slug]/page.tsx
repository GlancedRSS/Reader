'use client'

import { Container } from '@/components/articles/layout'
import { useParams } from 'next/navigation'

export default function FolderArticlesPage() {
	const params = useParams()
	return (
		<Container
			baseQuery={{ folder_ids: [params.slug as string] }}
			emptyType='all'
		/>
	)
}
