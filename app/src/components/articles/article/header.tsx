'use client'

import { ArticleMeta } from '@/components/articles/article/meta'

import { Skeleton } from '@/components/ui/skeleton'

import type { ArticleResponse } from '@/types/api'

export default function ArticleHeader({
	data,
	loading
}: {
	data: ArticleResponse | undefined
	loading: boolean
}) {
	const renderTitle = () => {
		if (loading) {
			return (
				<>
					<Skeleton className='h-9 w-full mb-2' />
					<Skeleton className='h-9 w-3/4 mb-4' />
				</>
			)
		}
		return (
			<h1 className='article-title text-4xl font-bold mb-4 font-branding'>
				{data?.title}
			</h1>
		)
	}

	return (
		<header className='mb-2'>
			{renderTitle()}

			<div className='flex flex-wrap items-center justify-between gap-6'>
				<ArticleMeta
					author={data?.author}
					loading={loading}
					publishedAt={data?.published_at}
					reading_time={data?.reading_time}
					subscription_id={data?.feeds?.[0]?.id}
					subscription_title={data?.feeds?.[0]?.title}
					website={data?.feeds?.[0]?.website}
				/>
			</div>
		</header>
	)
}
