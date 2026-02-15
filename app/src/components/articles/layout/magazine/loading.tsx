'use client'

import { memo } from 'react'

import { Skeleton } from '@/components/ui/skeleton'

import { useUserPreferences } from '@/hooks/api'
import { useSplitLayout } from '@/hooks/ui/layout'

function MagazineLoading() {
	const { data: preferences } = useUserPreferences()
	const { shouldShowSplitLayout } = useSplitLayout()

	if (!preferences) {
		return null
	}

	return (
		<div className='flex items-start space-x-4'>
			<div className='shrink-0'>
				{preferences?.show_article_thumbnails ? (
					<Skeleton
						className={`relative w-16 ${preferences?.show_summaries ? 'h-32' : 'h-18'} ${shouldShowSplitLayout ? '' : 'sm:w-32 sm:h-24 md:w-48 md:h-32'} rounded-lg`}
					/>
				) : null}
			</div>

			<div className='flex-1 min-w-0 space-y-2'>
				<Skeleton className='h-5 lg:h-5 w-full rounded' />
				<Skeleton className='h-5 lg:h-5 w-3/4 rounded' />

				{preferences?.show_summaries ? (
					<>
						<Skeleton className='h-4 w-full rounded max-md:hidden' />
						<Skeleton className='h-4 w-2/3 rounded' />
					</>
				) : null}

				<div className='flex gap-4 justify-between'>
					<div className='flex gap-2'>
						{preferences?.show_feed_favicons ? (
							<Skeleton className='size-4 rounded-full' />
						) : null}
						<Skeleton className='h-4 w-24' />
					</div>
					<Skeleton className='h-4 w-20 rounded' />
				</div>
			</div>
		</div>
	)
}

export default memo(MagazineLoading)
