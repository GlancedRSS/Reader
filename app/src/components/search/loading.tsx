'use client'

import { Skeleton } from '@/components/ui/skeleton'

function ArticleSkeleton() {
	return (
		<div className='flex items-center gap-3 w-full px-2 py-1.5'>
			<div className='shrink-0'>
				<Skeleton className='w-16 h-16 rounded' />
			</div>
			<div className='flex-1 min-w-0'>
				<div className='flex justify-between gap-2'>
					<Skeleton className='h-5 w-3/4' />
					<Skeleton className='h-5 w-12 rounded-full' />
				</div>
				<Skeleton className='h-4 w-full mt-1' />
				<div className='flex justify-between items-center gap-2 mt-1'>
					<Skeleton className='h-3.5 w-24' />
					<Skeleton className='h-3.5 w-12' />
				</div>
			</div>
		</div>
	)
}

function FeedSkeleton() {
	return (
		<div className='flex items-center gap-3 w-full px-2 py-1.5'>
			<div className='shrink-0'>
				<Skeleton className='w-10 h-10 rounded-full' />
			</div>
			<div className='flex-1 min-w-0 overflow-hidden'>
				<Skeleton className='h-5 w-1/2' />
				<Skeleton className='h-3.5 w-32 mt-1' />
			</div>
			<div className='min-w-0'>
				<Skeleton className='h-5 w-8 rounded-full' />
			</div>
		</div>
	)
}

function TagSkeleton() {
	return (
		<div className='flex items-center gap-3 w-full px-2 py-1.5'>
			<Skeleton className='w-6 h-6' />
			<div className='flex-1 min-w-0'>
				<Skeleton className='h-5 w-1/3' />
				<Skeleton className='h-3.5 w-20 mt-1' />
			</div>
		</div>
	)
}

function FolderSkeleton() {
	return (
		<div className='flex items-center gap-3 w-full px-2 py-1.5'>
			<Skeleton className='w-6 h-6' />
			<div className='flex-1 min-w-0'>
				<Skeleton className='h-5 w-1/3' />
				<Skeleton className='h-3.5 w-16 mt-1' />
			</div>
			<div className='min-w-0'>
				<Skeleton className='h-5 w-8 rounded-full' />
			</div>
		</div>
	)
}

interface SearchLoadingProps {
	count?: number
}

export function SearchLoading({ count = 4 }: SearchLoadingProps) {
	const skeletons = []

	for (let i = 0; i < count; i++) {
		const type = i % 4
		if (type === 0) {
			skeletons.push(<ArticleSkeleton key={`article-${i}`} />)
		} else if (type === 1) {
			skeletons.push(<FeedSkeleton key={`feed-${i}`} />)
		} else if (type === 2) {
			skeletons.push(<TagSkeleton key={`tag-${i}`} />)
		} else {
			skeletons.push(<FolderSkeleton key={`folder-${i}`} />)
		}
	}

	return <div className='flex flex-col gap-1'>{skeletons}</div>
}
