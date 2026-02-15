'use client'

import { Header } from '@/components/header'
import { RollbackModal } from '@/components/imports'
import { useState } from 'react'
import { IoArrowUndoOutline } from 'react-icons/io5'

import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'

import { useUserPreferences } from '@/hooks/api'
import useMetadata from '@/hooks/navigation/metadata'

import type { OpmlOperationResponse } from '@/types/api'
import type { OpmlStatus } from '@/types/opml'

import { formatTime } from '@/utils/article'
import { getOpmlStatus } from '@/utils/opml'

export function ImportInfo({
	data,
	loading
}: {
	data: OpmlOperationResponse | undefined
	loading: boolean
}) {
	const [isRollbackModalOpen, setIsRollbackModalOpen] = useState(false)
	const { data: preferences } = useUserPreferences()

	useMetadata(
		`${loading ? 'Loading...' : data?.filename || 'Import'} | Glanced Reader`
	)

	const renderStatus = (status: string) => {
		const { label, color, icon: Icon } = getOpmlStatus(status as OpmlStatus)
		return (
			<div className='flex items-center gap-1'>
				<Icon className={color} />
				<span>{label}</span>
			</div>
		)
	}

	const renderData = () => {
		if (data) {
			return (
				<Card className='p-4 gap-2'>
					<div className='grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-2'>
						<div className='flex justify-between gap-4'>
							<span className='font-semibold shrink-0'>Filename</span>
							<span className='text-muted-foreground truncate'>
								{data?.filename}
							</span>
						</div>
						<div className='flex justify-between'>
							<span className='font-semibold'>Status</span>
							<span className='text-muted-foreground'>
								{renderStatus(data?.status)}
							</span>
						</div>
						<div className='flex justify-between'>
							<span className='font-semibold'>Feeds</span>
							<span className='text-muted-foreground'>
								{data?.total_feeds || '-'}
							</span>
						</div>
						<div className='flex justify-between'>
							<span className='font-semibold'>Imported</span>
							<span className='text-muted-foreground'>
								{data?.imported_feeds ?? '-'}
							</span>
						</div>
						<div className='flex justify-between'>
							<span className='font-semibold'>Duplicates</span>
							<span className='text-muted-foreground'>
								{data?.duplicate_feeds ?? '-'}
							</span>
						</div>
						<div className='flex justify-between'>
							<span className='font-semibold'>Failed</span>
							<span className='text-muted-foreground'>
								{data?.failed_feeds ?? '-'}
							</span>
						</div>
						<div className='flex justify-between'>
							<span className='font-semibold'>Started</span>
							<span className='text-muted-foreground'>
								{data?.created_at
									? formatTime(
											data.created_at,
											preferences?.date_format === 'absolute'
												? 'absolute'
												: 'relative',
											preferences?.time_format === '24h' ? '24h' : '12h',
											true
										)
									: '-'}
							</span>
						</div>
						<div className='flex justify-between'>
							<span className='font-semibold'>Completion</span>
							<span className='text-muted-foreground'>
								{data?.completed_at
									? formatTime(
											data.completed_at,
											preferences?.date_format === 'absolute'
												? 'absolute'
												: 'relative',
											preferences?.time_format === '24h' ? '24h' : '12h',
											true
										)
									: '-'}
							</span>
						</div>
					</div>
				</Card>
			)
		}
		return (
			<Skeleton className='h-[calc(8*&1.5rem+7*0.5rem+2rem+2px)] md:h-[calc(4*1.5rem+3*0.5rem+2rem+2px)] w-full rounded-xl' />
		)
	}

	return (
		<>
			<div className='flex'>
				<Header
					className='flex-1'
					title={
						loading
							? 'Loading...'
							: `${data?.type?.[0]?.toUpperCase().concat(data?.type?.slice(1, data?.type?.length))} Operation` ||
								'Import'
					}
				/>
				{!loading &&
				data?.type === 'import' &&
				data?.completed_at &&
				data?.imported_feeds ? (
					<div className='p-4'>
						<Button
							onClick={() => setIsRollbackModalOpen(true)}
							size='sm'
							variant='ghost'
						>
							<IoArrowUndoOutline className='md:hidden' />
							<span className='max-md:hidden'>Rollback</span>
						</Button>
					</div>
				) : null}
			</div>
			<div className='px-4'>{renderData()}</div>
			{!loading && data?.type === 'import' ? (
				<RollbackModal
					importCount={data?.imported_feeds ?? 0}
					importId={data?.id ?? ''}
					isOpen={isRollbackModalOpen}
					onOpenChange={setIsRollbackModalOpen}
				/>
			) : null}
		</>
	)
}
