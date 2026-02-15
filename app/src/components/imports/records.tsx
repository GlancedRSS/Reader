'use client'

import { parseFeedError } from '@/components/imports/utils'
import { AvatarFallback } from '@radix-ui/react-avatar'
import { useEffect, useState } from 'react'
import { IoChevronBack, IoChevronForward } from 'react-icons/io5'

import { Avatar, AvatarImage } from '@/components/ui/avatar'
import { Button } from '@/components/ui/button'
import {
	Table,
	TableBody,
	TableCell,
	TableHead,
	TableHeader,
	TableRow
} from '@/components/ui/table'
import {
	Tooltip,
	TooltipContent,
	TooltipProvider,
	TooltipTrigger
} from '@/components/ui/tooltip'

import type { OpmlOperationResponse } from '@/types/api'

import { getDomain } from '@/utils/url'

interface FeedLogItem {
	title: string
	url: string
	error: string
}

const PAGE_SIZE = 20

export function ImportRecords({
	data
}: {
	data: OpmlOperationResponse | undefined
}) {
	const [currentPage, setCurrentPage] = useState(1)
	const failedFeeds = (data?.failed_feeds_log as FeedLogItem[]) || []

	const totalFeeds = failedFeeds.length
	const totalPages = Math.ceil(totalFeeds / PAGE_SIZE) || 1
	const startIndex = (currentPage - 1) * PAGE_SIZE
	const endIndex = startIndex + PAGE_SIZE
	const paginatedFeeds = failedFeeds.slice(startIndex, endIndex)
	const hasMore = endIndex < totalFeeds

	const handlePreviousPage = () => {
		setCurrentPage((prev) => Math.max(1, prev - 1))
	}

	const handleNextPage = () => {
		setCurrentPage((prev) => (hasMore ? prev + 1 : prev))
	}

	useEffect(() => {
		setCurrentPage(1)
	}, [data?.failed_feeds_log])

	if (!data || failedFeeds.length === 0) {
		return null
	}

	return (
		<div className='px-4 pt-4 '>
			<div className='border rounded-xl max-h-[calc(100dvh-4.25rem-7rem-(8*1.5rem+7*0.5rem+2rem+2px+0.75rem))] md:max-h-[calc(100dvh-4.25rem-(4*1.5rem+3*0.5rem+2rem+2px+4rem))] overflow-scroll'>
				<Table>
					<TableHeader className='bg-sidebar-background'>
						<TableRow>
							<TableHead>Feed</TableHead>
							<TableHead>Status</TableHead>
						</TableRow>
					</TableHeader>
					<TableBody>
						{paginatedFeeds.map((feed, index) => (
							<TableRow
								className='cursor-pointer hover:bg-accent hover:text-accent-foreground'
								key={feed.url || index}
								onClick={() =>
									window.open(feed.url, '_blank', 'noopener,noreferrer')
								}
							>
								<TableCell className='flex gap-3'>
									<div className='flex flex-col justify-center'>
										<Avatar className='size-5 shrink-0'>
											<AvatarImage
												alt={feed.title}
												src={`https://www.google.com/s2/favicons?domain=${getDomain(feed.url)}&sz=64`}
											/>
											<AvatarFallback className='text-xs'>
												{feed.title[0]}
											</AvatarFallback>
										</Avatar>
									</div>
									<div className='max-w-xl'>
										<div className='font-medium line-clamp-1'>
											{feed.title || 'Untitled Feed'}
										</div>
										<div className='text-sm text-muted-foreground truncate'>
											{feed.url || '-'}
										</div>
									</div>
								</TableCell>
								<TableCell>
									<TooltipProvider>
										<Tooltip>
											<TooltipTrigger asChild>
												<div className='flex items-center gap-2 min-w-40'>
													{parseFeedError(feed.error).message}
												</div>
											</TooltipTrigger>
											<TooltipContent
												className='max-w-md'
												side='bottom'
											>
												<p className='text-xs whitespace-pre-wrap'>
													{feed.error}
												</p>
											</TooltipContent>
										</Tooltip>
									</TooltipProvider>
								</TableCell>
							</TableRow>
						))}
					</TableBody>
				</Table>
			</div>

			{totalPages > 1 && (
				<div className='flex items-center justify-between max-md:justify-end pt-3'>
					<span className='text-sm text-muted-foreground max-md:hidden'>
						Showing {paginatedFeeds.length > 0 ? startIndex + 1 : 0} -{' '}
						{Math.min(endIndex, totalFeeds)} of {totalFeeds} feed
						{totalFeeds !== 1 ? 's' : ''}
					</span>
					<div className='flex items-center gap-2'>
						<span className='text-sm text-muted-foreground'>
							Page {currentPage} of {totalPages}
						</span>
						<div className='flex gap-1'>
							<Button
								className='h-7 sm:h-5'
								disabled={currentPage === 1}
								onClick={handlePreviousPage}
								size='sm'
								type='button'
								variant='ghost'
							>
								<IoChevronBack className='size-4' />
							</Button>
							<Button
								className='h-7 sm:h-5'
								disabled={!hasMore}
								onClick={handleNextPage}
								size='sm'
								type='button'
								variant='ghost'
							>
								<IoChevronForward className='size-4' />
							</Button>
						</div>
					</div>
				</div>
			)}
		</div>
	)
}
