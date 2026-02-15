'use client'

import { Welcome } from '@/components/welcome'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'

import { useFeeds } from '@/hooks/api/feeds'

export default function DashboardPage() {
	const router = useRouter()
	const { data: feedsData } = useFeeds({ all: true })

	useEffect(() => {
		if (feedsData && feedsData.data.length > 0) {
			router.replace('/articles')
		}
	}, [feedsData, router])

	if (feedsData && feedsData.data.length === 0) {
		return <Welcome />
	}

	return null
}
