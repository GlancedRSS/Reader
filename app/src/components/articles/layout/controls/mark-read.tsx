'use client'

import { useArticlesPaginationStore } from '@/stores/articles-pagination'
import { usePathname } from 'next/navigation'
import { useState } from 'react'
import { IoCheckmarkDoneOutline } from 'react-icons/io5'
import { toast } from 'sonner'
import { useSWRConfig } from 'swr'

import { Button } from '@/components/ui/button'
import {
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuItem,
	DropdownMenuTrigger
} from '@/components/ui/dropdown-menu'

import { useMarkAllAsRead } from '@/hooks/api'

import { MarkAllReadRequest } from '@/types/api'

export function MarkReadDropdown() {
	const pathname = usePathname()
	const { mutate } = useSWRConfig()
	const markAllAsRead = useMarkAllAsRead()
	const refreshArticles = useArticlesPaginationStore(
		(state) => state.refreshArticles
	)

	const {
		q,
		is_read,
		read_later,
		folderOptions,
		subscriptionOptions,
		tagOptions,
		from_date,
		to_date
	} = useArticlesPaginationStore()

	const [isMarking, setIsMarking] = useState(false)

	const isReadPath = pathname.includes('/read')
		? 'read'
		: pathname.includes('/unread')
			? 'unread'
			: 'all'

	const isReadLaterRoute = pathname.includes('/read-later')
	const isFeedRoute = pathname.includes('/feeds/')
	const isFolderRoute = pathname.includes('/folders/')
	const isTagRoute = pathname.includes('/tags/')

	const subscriptionId = isFeedRoute
		? pathname.split('/feeds/')[1]?.split('/')[0]
		: undefined
	const folderId = isFolderRoute
		? pathname.split('/folders/')[1]?.split('/')[0]
		: undefined
	const tagId = isTagRoute
		? pathname.split('/tags/')[1]?.split('/')[0]
		: undefined

	const buildFilters = (isReadValue: boolean): MarkAllReadRequest => {
		const filters: MarkAllReadRequest = {
			is_read: isReadValue
		}

		const hasStoreFilters =
			q ||
			is_read !== 'all' ||
			read_later !== 'all' ||
			folderOptions.length > 0 ||
			subscriptionOptions.length > 0 ||
			tagOptions.length > 0 ||
			from_date ||
			to_date

		if (hasStoreFilters) {
			if (is_read !== 'all') filters.is_read_filter = is_read
			if (read_later !== 'all') filters.read_later = read_later
			if (q) filters.q = q
			if (from_date) filters.from_date = from_date
			if (to_date) filters.to_date = to_date
			if (folderOptions.length > 0)
				filters.folder_ids = folderOptions.map((o) => o.value)
			if (subscriptionOptions.length > 0)
				filters.subscription_ids = subscriptionOptions.map((o) => o.value)
			if (tagOptions.length > 0)
				filters.tag_ids = tagOptions.map((o) => o.value)

			return filters
		}

		if (isReadLaterRoute) {
			filters.read_later = 'true'
		}

		if (subscriptionId) filters.subscription_ids = [subscriptionId]
		if (folderId) filters.folder_ids = [folderId]
		if (tagId) filters.tag_ids = [tagId]

		return filters
	}

	const handleMarkAllAsRead = async () => {
		setIsMarking(true)
		try {
			await markAllAsRead.markAsRead(buildFilters(true))

			await mutate(
				(key) => typeof key === 'string' && key.startsWith('/articles')
			)

			await mutate((key) => typeof key === 'string' && key.startsWith('/feeds'))

			await mutate('/folders/tree')

			refreshArticles()

			toast.success('Marked all as read')
		} catch (error) {
			console.error('Failed to mark all as read:', error)
			toast.error('Failed to mark articles as read')
		} finally {
			setIsMarking(false)
		}
	}

	const handleMarkAllAsUnread = async () => {
		setIsMarking(true)
		try {
			await markAllAsRead.markAsRead(buildFilters(false))

			await mutate(
				(key) => typeof key === 'string' && key.startsWith('/articles')
			)

			await mutate((key) => typeof key === 'string' && key.startsWith('/feeds'))

			await mutate('/folders/tree')

			refreshArticles()

			toast.success('Marked all as unread')
		} catch (error) {
			console.error('Failed to mark as unread:', error)
			toast.error('Failed to mark articles as unread')
		} finally {
			setIsMarking(false)
		}
	}

	return (
		<DropdownMenu>
			<DropdownMenuTrigger asChild>
				<Button
					disabled={isMarking}
					size='sm'
					title='Mark articles as read'
					variant='ghost'
				>
					<IoCheckmarkDoneOutline className='h-4 w-4' />
				</Button>
			</DropdownMenuTrigger>
			<DropdownMenuContent>
				{isReadPath !== 'read' && (
					<DropdownMenuItem
						disabled={isMarking}
						onClick={handleMarkAllAsRead}
					>
						<span className='flex items-center gap-2'>
							<IoCheckmarkDoneOutline className='h-4 w-4' />
							Mark all as read
						</span>
					</DropdownMenuItem>
				)}

				{isReadPath !== 'unread' && (
					<DropdownMenuItem
						disabled={isMarking}
						onClick={handleMarkAllAsUnread}
					>
						<span className='flex items-center gap-2'>
							<IoCheckmarkDoneOutline className='h-4 w-4' />
							Mark all as unread
						</span>
					</DropdownMenuItem>
				)}
			</DropdownMenuContent>
		</DropdownMenu>
	)
}
