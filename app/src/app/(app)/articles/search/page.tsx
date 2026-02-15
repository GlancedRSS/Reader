'use client'

import { Container } from '@/components/articles/layout'
import { useArticlesPaginationStore } from '@/stores/articles-pagination'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'

export default function ArticlesSearchPage() {
	const router = useRouter()

	const {
		q,
		is_read,
		read_later,
		folderOptions,
		subscriptionOptions,
		tagOptions,
		from_date,
		to_date
	} = useArticlesPaginationStore()

	const hasActiveFilters =
		q ||
		is_read !== 'all' ||
		read_later !== 'all' ||
		folderOptions.length > 0 ||
		subscriptionOptions.length > 0 ||
		tagOptions.length > 0 ||
		from_date ||
		to_date

	useEffect(() => {
		if (!hasActiveFilters) {
			router.push('/articles')
		}
	}, [hasActiveFilters, router])

	if (!hasActiveFilters) return null

	return <Container emptyType='search' />
}
