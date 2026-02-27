'use client'

import { SessionCard } from '@/components/settings/account/sessions/session'
import { useEffect, useState } from 'react'
import { IoChevronBack, IoChevronForward } from 'react-icons/io5'
import { toast } from 'sonner'

import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'

import { revokeSession, useSessions } from '@/hooks/api'

import type { SessionResponse } from '@/types/api'

const pageSize = 3

export function SessionList() {
	const { data, isLoading, mutate } = useSessions()
	const sessions = data?.data || []
	const [isRevoking, setIsRevoking] = useState<string | null>(null)
	const [failedImages, setFailedImages] = useState<Set<string>>(new Set())
	const [currentPage, setCurrentPage] = useState(1)

	const totalPages = sessions ? Math.ceil(sessions.length / pageSize) : 0
	const paginatedSessions = sessions
		? sessions.slice((currentPage - 1) * pageSize, currentPage * pageSize)
		: []

	const handlePreviousPage = () => {
		setCurrentPage((prev) => Math.max(1, prev - 1))
	}

	const handleNextPage = () => {
		setCurrentPage((prev) => Math.min(totalPages, prev + 1))
	}

	useEffect(() => {
		if (totalPages > 0 && currentPage > totalPages) {
			setCurrentPage(1)
		}
	}, [totalPages, currentPage])

	const handleRevoke = async (sessionId: string) => {
		setIsRevoking(sessionId)
		try {
			await revokeSession(sessionId)
			toast.success('Session revoked successfully')
			await mutate()
		} catch (error) {
			toast.error(
				error instanceof Error ? error.message : 'Failed to revoke session'
			)
		} finally {
			setIsRevoking(null)
		}
	}

	const handleImageError = (sessionId: string) => {
		setFailedImages((prev) => new Set(prev).add(sessionId))
	}

	return (
		<div className='space-y-3'>
			<div className='flex items-center justify-between'>
				<h3 className='text-base font-semibold'>Sessions</h3>
				{totalPages > 1 && (
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
								disabled={currentPage === totalPages}
								onClick={handleNextPage}
								size='sm'
								type='button'
								variant='ghost'
							>
								<IoChevronForward className='size-4' />
							</Button>
						</div>
					</div>
				)}
			</div>

			{isLoading ? (
				<>
					{Array.from({ length: 3 }).map((i, index) => (
						<Card
							className='px-3 py-2 gap-2'
							key={index}
						>
							<div className='flex items-center justify-between'>
								<div className='flex items-center space-x-4 flex-1'>
									<Skeleton className='h-8 w-8 rounded' />
									<div className='flex flex-1 items-center gap-3'>
										<div>
											<Skeleton className='h-5 w-32 mb-2' />
											<Skeleton className='h-4 w-40' />
										</div>
									</div>
									<Skeleton className='h-8 w-8 rounded' />
								</div>
							</div>
						</Card>
					))}
				</>
			) : sessions && sessions.length === 0 ? (
				<div className='text-sm text-muted-foreground'>No active sessions.</div>
			) : (
				paginatedSessions.map((session: SessionResponse) => (
					<SessionCard
						failedImages={failedImages}
						isLoading={isLoading}
						isRevoking={isRevoking === session.session_id}
						key={session.session_id}
						onImageError={handleImageError}
						onRevoke={handleRevoke}
						session={session}
					/>
				))
			)}
		</div>
	)
}
