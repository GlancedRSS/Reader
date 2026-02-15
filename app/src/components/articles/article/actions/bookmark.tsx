'use client'

import { forwardRef, useEffect, useImperativeHandle, useState } from 'react'
import { IoBookmark, IoBookmarkOutline } from 'react-icons/io5'
import { toast } from 'sonner'
import { useSWRConfig } from 'swr'

import { Button } from '@/components/ui/button'
import { Hotkey } from '@/components/ui/hotkey'
import {
	Tooltip,
	TooltipContent,
	TooltipTrigger
} from '@/components/ui/tooltip'

import type { ArticleResponse } from '@/types/api'

interface BookmarkProps {
	articleId: string
	readLater?: boolean
	updateArticleState: ReturnType<
		typeof import('@/hooks/api').useUpdateArticleState
	>
}

export interface BookmarkRef {
	trigger: () => void
}

export const Bookmark = forwardRef<BookmarkRef, BookmarkProps>(
	({ articleId, readLater, updateArticleState }, ref) => {
		const { mutate: swrMutate, cache } = useSWRConfig()
		const [isReadLater, setIsReadLater] = useState(readLater || false)

		useImperativeHandle(ref, () => ({
			trigger: handleReadLaterClick
		}))

		useEffect(() => {
			if (readLater !== undefined) {
				setIsReadLater(readLater)
			}
		}, [readLater])

		const handleReadLaterClick = async () => {
			const newReadLaterState = !isReadLater
			setIsReadLater(newReadLaterState)

			try {
				await updateArticleState.mutate({ read_later: newReadLaterState })
				const articleKey = `/articles/${articleId}`
				const currentArticle = cache.get(articleKey)
				if (currentArticle?.data) {
					swrMutate(
						articleKey,
						{
							...(currentArticle.data as ArticleResponse),
							read_later: newReadLaterState
						},
						false
					)
				} else {
					await swrMutate(articleKey)
				}
				toast.success(
					newReadLaterState ? 'Added to read later' : 'Removed from read later'
				)
			} catch (error) {
				setIsReadLater(!newReadLaterState)
				toast.error('Failed to update read later state')
				console.error('Failed to update read later:', error)
			}
		}

		return (
			<Tooltip>
				<TooltipTrigger asChild>
					<Button
						className='flex items-center gap-2 px-4 py-2'
						onClick={handleReadLaterClick}
						size='icon'
						variant='outline'
					>
						{isReadLater ? (
							<IoBookmark className='w-4 h-4' />
						) : (
							<IoBookmarkOutline className='w-4 h-4' />
						)}
					</Button>
				</TooltipTrigger>
				<TooltipContent
					className='flex gap-2'
					sideOffset={4}
				>
					<Hotkey>S</Hotkey>
					<div className='flex items-center'>
						{isReadLater ? 'Remove from' : 'Add to'} Read Later
					</div>
				</TooltipContent>
			</Tooltip>
		)
	}
)

Bookmark.displayName = 'Bookmark'
