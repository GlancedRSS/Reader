'use client'

import * as TooltipPrimitive from '@radix-ui/react-tooltip'
import { forwardRef, useCallback, useImperativeHandle, useState } from 'react'
import { FaRedditAlien, FaXTwitter } from 'react-icons/fa6'
import {
	IoCopyOutline,
	IoMailOutline,
	IoShareSocialOutline
} from 'react-icons/io5'
import { toast } from 'sonner'

import { Button } from '@/components/ui/button'
import {
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuItem,
	DropdownMenuTrigger
} from '@/components/ui/dropdown-menu'
import { TooltipContent, TooltipTrigger } from '@/components/ui/tooltip'

interface ShareProps {
	link: string | undefined
	title?: string | undefined
}

export interface ShareRef {
	trigger: () => void
}

export const Share = forwardRef<ShareRef, ShareProps>(
	({ link, title }, ref) => {
		const [open, setOpen] = useState(false)
		const [isSharing, setIsSharing] = useState(false)

		const canShare = typeof navigator !== 'undefined' && 'share' in navigator

		const handleWebShare = useCallback(async () => {
			if (!link || isSharing) return

			setIsSharing(true)
			try {
				await navigator.share({
					title: title || 'Check out this article',
					url: link
				})
			} catch (error) {
				if ((error as Error).name !== 'AbortError') {
					console.error('Share failed:', error)
				}
			} finally {
				setIsSharing(false)
			}
		}, [link, title, isSharing])

		const handleButtonClick = useCallback(
			async (e: React.MouseEvent) => {
				if (!canShare || isSharing) return

				e.preventDefault()
				e.stopPropagation()
				await handleWebShare()
			},
			[canShare, isSharing, handleWebShare]
		)

		const handleShareClick = useCallback(async () => {
			if (canShare) {
				await handleWebShare()
				return
			}
			setOpen(true)
		}, [canShare, handleWebShare])

		useImperativeHandle(ref, () => ({
			trigger: handleShareClick
		}))

		const handleOpenChange = useCallback(
			(newOpen: boolean) => {
				if (canShare && newOpen) {
					setOpen(false)
					return
				}
				setOpen(newOpen)
			},
			[canShare]
		)

		const handleShare = async (platform: string) => {
			if (!link) return

			const encodedUrl = encodeURIComponent(link)
			const shareTitle = title || 'Check out this article'
			const encodedTitle = encodeURIComponent(shareTitle)

			try {
				switch (platform) {
					case 'link':
						await navigator.clipboard.writeText(link)
						toast.success('Link copied to clipboard')
						break
					case 'twitter':
						window.open(
							`https://x.com/intent/tweet?url=${encodedUrl}&text=${encodedTitle}`,
							'_blank',
							'noopener,noreferrer'
						)
						break
					case 'reddit':
						window.open(
							`https://www.reddit.com/submit?url=${encodedUrl}&title=${encodedTitle}`,
							'_blank',
							'noopener,noreferrer'
						)
						break
					case 'email':
						window.open(
							`mailto:?subject=${encodedTitle}&body=${encodedUrl}`,
							'_blank'
						)
						break
				}
			} catch (error) {
				if (platform === 'link') {
					toast.error('Failed to copy link to clipboard')
				} else {
					toast.error('Failed to share article')
				}
				console.error('Share error:', error)
			}
		}

		return (
			<TooltipPrimitive.Root>
				<DropdownMenu
					onOpenChange={handleOpenChange}
					open={open}
				>
					<DropdownMenuTrigger asChild>
						<TooltipTrigger asChild>
							<Button
								className='flex items-center gap-2 px-4 py-2'
								disabled={!link}
								onClick={canShare ? handleButtonClick : undefined}
								size='icon'
								variant='outline'
							>
								<IoShareSocialOutline className='w-4 h-4' />
							</Button>
						</TooltipTrigger>
					</DropdownMenuTrigger>
					<DropdownMenuContent
						align='start'
						className='w-48'
					>
						<DropdownMenuItem
							className='cursor-pointer'
							onClick={() => handleShare('link')}
						>
							<IoCopyOutline className='w-4 h-4 mr-2' />
							Copy link
						</DropdownMenuItem>
						<DropdownMenuItem
							className='cursor-pointer'
							onClick={() => handleShare('twitter')}
						>
							<FaXTwitter className='w-4 h-4 mr-2' />
							Share on X
						</DropdownMenuItem>
						<DropdownMenuItem
							className='cursor-pointer'
							onClick={() => handleShare('reddit')}
						>
							<FaRedditAlien className='w-4 h-4 mr-2' />
							Share on Reddit
						</DropdownMenuItem>
						<DropdownMenuItem
							className='cursor-pointer'
							onClick={() => handleShare('email')}
						>
							<IoMailOutline className='w-4 h-4 mr-2' />
							Share via Email
						</DropdownMenuItem>
					</DropdownMenuContent>
				</DropdownMenu>
				<TooltipContent
					className='flex gap-2'
					sideOffset={4}
				>
					<div className='flex items-center'>Share article</div>
				</TooltipContent>
			</TooltipPrimitive.Root>
		)
	}
)

Share.displayName = 'Share'
