'use client'

import { memo } from 'react'

import { Skeleton } from '@/components/ui/skeleton'

import { useUserPreferences } from '@/hooks/api'

function ListLoading() {
	const { data: preferences } = useUserPreferences()

	if (!preferences) {
		return null
	}

	return (
		<div className='group flex items-start space-x-2 py-2 border-b last-of-type:border-b-0 px-2'>
			<div className='shrink-0'>
				{preferences?.show_article_thumbnails ? (
					<div
						className={`relative ${preferences?.show_summaries ? 'w-16 h-16' : 'w-10 h-10'} rounded-md overflow-hidden`}
					>
						<Skeleton className='w-full h-full rounded-md' />
					</div>
				) : null}
			</div>

			<div className='flex-1 min-w-0'>
				<div className='mb-1'>
					<Skeleton className='h-5 w-4/5' />
				</div>

				<div className='flex items-center justify-between'>
					<div className='flex gap-2'>
						{preferences?.show_feed_favicons ? (
							<Skeleton className='size-4 rounded-full' />
						) : null}
						<Skeleton className='h-4 w-24' />
					</div>
					<Skeleton className='h-4 w-12 shrink-0' />
				</div>

				{preferences?.show_summaries ? (
					<div className='mt-1'>
						<Skeleton className='h-4 w-3/4' />
					</div>
				) : null}
			</div>
		</div>
	)
}

export default memo(ListLoading)
