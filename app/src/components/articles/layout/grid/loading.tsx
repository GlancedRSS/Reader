'use client'

import { memo } from 'react'

import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Card, CardContent } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'

import { useUserPreferences } from '@/hooks/api'

function GridLoading() {
	const { data: preferences } = useUserPreferences()

	if (!preferences) {
		return null
	}

	return (
		<Card className='group relative overflow-hidden transition-all duration-300 ease-out py-0 gap-0 border hover:border-accent dark:hover:border-accent shadow-lg shadow-black/5 dark:shadow-white/10 hover:shadow-xl hover:shadow-black/10 dark:hover:shadow-white/20'>
			{preferences?.show_article_thumbnails ? (
				<div className='relative'>
					<Skeleton className='relative h-48 rounded-none' />
				</div>
			) : null}

			<CardContent className='px-4 pb-2 pt-4'>
				<div className='flex items-center justify-between mb-3'>
					<div className='flex items-center gap-2'>
						{preferences?.show_feed_favicons ? (
							<Avatar className='size-5 shrink-0'>
								<AvatarFallback className='bg-accent'>
									<Skeleton className='size-5 rounded-full' />
								</AvatarFallback>
							</Avatar>
						) : null}
						<Skeleton className='h-4 w-24' />
					</div>
					<Skeleton className='h-4 w-12' />
				</div>

				<div className='mb-3 h-11'>
					<Skeleton className='h-11 w-4/5' />
				</div>

				{preferences?.show_summaries ? (
					<div className='mb-3 h-10'>
						<Skeleton className='h-10 w-full' />
					</div>
				) : null}
			</CardContent>
		</Card>
	)
}

export default memo(GridLoading)
