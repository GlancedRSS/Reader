'use client'

import {
	getBrowserLogo,
	parseUserAgent
} from '@/components/settings/account/sessions/utils'
import Image from 'next/image'
import { IoLogOutOutline } from 'react-icons/io5'

import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Pill } from '@/components/ui/pill'

import type { SessionResponse } from '@/types/api'

import { safeFormatDistanceToNow } from '@/utils/settings'

interface SessionCardProps {
	session: SessionResponse
	isRevoking: boolean
	isLoading: boolean
	failedImages: Set<string>
	onImageError: (sessionId: string) => void
	onRevoke: (sessionId: string) => void
}

export function SessionCard({
	session,
	isRevoking,
	isLoading,
	failedImages,
	onImageError,
	onRevoke
}: SessionCardProps) {
	const isCurrentSession = session.current
	const userAgent = session.user_agent || 'Unknown'
	const { browser, os } = parseUserAgent(userAgent)
	const imageSrc = failedImages.has(session.session_id)
		? '/browsers/generic.svg'
		: getBrowserLogo(browser)

	const lastUsed = new Date(session.last_used)

	return (
		<Card
			className='px-3 py-2'
			key={session.session_id}
		>
			<div className='flex items-center justify-between gap-3'>
				<div className='flex items-center gap-3 flex-1 w-0'>
					<Image
						alt={browser}
						className='object-contain shrink-0'
						height={32}
						onError={() => onImageError(session.session_id)}
						sizes='32px'
						src={imageSrc}
						width={32}
					/>

					<div className='flex-1 w-0'>
						<h3 className='font-semibold truncate'>
							{browser} on {os}
						</h3>

						<div className='text-sm text-muted-foreground/80 sm:flex sm:items-center gap-1'>
							<p className='truncate'>{safeFormatDistanceToNow(lastUsed)}</p>
							<span className='hidden sm:inline'>•</span>
							<p className='truncate'>{session.ip_address || 'Unknown'}</p>
						</div>
					</div>
				</div>
				{isCurrentSession ? <Pill>Current</Pill> : null}
				{!isCurrentSession && (
					<Button
						disabled={isRevoking || isLoading}
						onClick={() => onRevoke(session.session_id)}
						size='icon'
						variant='ghost'
					>
						<IoLogOutOutline className='w-4 h-4' />
					</Button>
				)}
			</div>
		</Card>
	)
}
