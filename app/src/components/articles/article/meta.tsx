'use client'

import Link from 'next/link'
import { useState } from 'react'
import {
	IoCalendarOutline,
	IoPersonOutline,
	IoTimeOutline
} from 'react-icons/io5'

import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Skeleton } from '@/components/ui/skeleton'

import { useUserPreferences } from '@/hooks/api'

import { formatTime } from '@/utils/article'
import { getLogoUrl } from '@/utils/logo'

export function ArticleMeta({
	author,
	website,
	loading,
	publishedAt,
	reading_time,
	subscription_id,
	subscription_title
}: {
	author: string | undefined
	website: string | undefined
	loading: boolean
	publishedAt: string | undefined
	reading_time: number | undefined
	subscription_id: string | undefined
	subscription_title: string | undefined
}) {
	const { data: preferences } = useUserPreferences()
	const [logoError, setLogoError] = useState(false)
	const logoUrl = website ? getLogoUrl(website) : null
	const currentLogo = logoError ? null : logoUrl

	if (loading) {
		return (
			<div className='flex flex-col sm:flex-row sm:flex-wrap items-center gap-2 sm:gap-3 text-sm text-muted-foreground w-full'>
				<div className='flex items-center justify-between sm:justify-start gap-3 w-full sm:w-auto'>
					<div className='flex items-center gap-2 min-w-[100px] max-w-40 sm:max-w-80'>
						<Skeleton className='size-6 rounded-full' />
						<Skeleton className='h-5 w-32' />
					</div>
					<div className='flex items-center gap-2 max-w-[150px]'>
						<Skeleton className='w-4 h-4' />
						<Skeleton className='h-5 w-24' />
					</div>
				</div>
				<div className='flex items-center justify-between sm:justify-start gap-3 w-full sm:w-auto'>
					<div className='flex items-center gap-2'>
						<Skeleton className='w-4 h-4' />
						<Skeleton className='h-5 w-20' />
					</div>
					<div className='flex items-center gap-2'>
						<Skeleton className='w-4 h-4' />
						<Skeleton className='h-5 w-16' />
					</div>
				</div>
			</div>
		)
	}

	return (
		<div className='flex flex-col sm:flex-row sm:flex-wrap items-center gap-2 sm:gap-3 text-sm text-muted-foreground w-full'>
			<div className='flex items-center justify-between sm:justify-start gap-3 w-full sm:w-auto'>
				<Link
					aria-label={`View more from ${subscription_title}`}
					className='flex items-center gap-2 hover:text-accent-foreground transition-colors min-w-[100px] max-w-40 sm:max-w-80'
					href={`/feeds/${subscription_id}`}
					title={subscription_title}
				>
					<Avatar className='size-5 shrink-0'>
						<AvatarImage
							alt={subscription_title}
							onError={() => setLogoError(true)}
							src={currentLogo || ''}
						/>
						<AvatarFallback className='text-xs'>
							{subscription_title?.slice(0, 2).toUpperCase()}
						</AvatarFallback>
					</Avatar>
					<span className='truncate'>{subscription_title}</span>
				</Link>
				{author ? (
					<div className='flex items-center gap-2 max-w-[150px]'>
						<IoPersonOutline
							aria-hidden='true'
							className='w-4 h-4 shrink-0'
						/>
						<span
							className='truncate'
							title={author}
						>
							{author}
						</span>
					</div>
				) : null}
			</div>
			<div className='flex items-center justify-between sm:justify-start gap-3 w-full sm:w-auto'>
				{publishedAt ? (
					<div className='flex items-center gap-2 shrink-0'>
						<IoCalendarOutline
							aria-hidden='true'
							className='w-4 h-4 shrink-0'
						/>
						<time dateTime={publishedAt}>
							{formatTime(
								publishedAt,
								preferences?.date_format || 'relative',
								preferences?.time_format || '12h'
							)}
						</time>
					</div>
				) : null}
				{preferences?.estimated_reading_time && reading_time ? (
					<div className='flex items-center gap-2 shrink-0'>
						<IoTimeOutline
							aria-hidden='true'
							className='w-4 h-4 shrink-0'
						/>
						<span>{reading_time} min read</span>
					</div>
				) : null}
			</div>
		</div>
	)
}
