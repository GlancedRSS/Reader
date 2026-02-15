'use client'

import { useArticlesPaginationStore } from '@/stores/articles-pagination'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { IoFilter } from 'react-icons/io5'

import { GenericAsyncSelect } from '@/components/ui/async-select'
import { Button } from '@/components/ui/button'
import {
	Dialog,
	DialogContent,
	DialogDescription,
	DialogFooter,
	DialogHeader,
	DialogTitle
} from '@/components/ui/dialog'
import {
	Drawer,
	DrawerClose,
	DrawerContent,
	DrawerDescription,
	DrawerFooter,
	DrawerHeader,
	DrawerTitle
} from '@/components/ui/drawer'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { ScrollArea } from '@/components/ui/scroll-area'
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue
} from '@/components/ui/select'

import { searchTags } from '@/hooks/api/tags'
import { useIsMobile } from '@/hooks/ui/media-query'

import { apiClient } from '@/lib/api'

import type { SelectOption } from '@/components/ui/async-select'
import type { FeedSearchResponse, FolderSearchResponse } from '@/types/api'

export function Filters() {
	const isMobile = useIsMobile()
	const router = useRouter()
	const [isOpen, setIsOpen] = useState(false)

	const store = useArticlesPaginationStore()

	const [localQ, setLocalQ] = useState('')
	const [localReadLater, setLocalReadLater] = useState<
		'all' | 'true' | 'false'
	>('all')
	const [localFolderOptions, setLocalFolderOptions] = useState<SelectOption[]>(
		[]
	)
	const [localSubscriptionOptions, setLocalSubscriptionOptions] = useState<
		SelectOption[]
	>([])
	const [localTagOptions, setLocalTagOptions] = useState<SelectOption[]>([])
	const [localFromDate, setLocalFromDate] = useState('')
	const [localToDate, setLocalToDate] = useState('')

	// Sync local state from store when dialog opens
	useEffect(() => {
		if (isOpen) {
			setLocalQ(store.q)
			setLocalReadLater(store.read_later)
			setLocalFolderOptions(store.folderOptions)
			setLocalSubscriptionOptions(store.subscriptionOptions)
			setLocalTagOptions(store.tagOptions)
			setLocalFromDate(store.from_date)
			setLocalToDate(store.to_date)
		}
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, [isOpen])

	const loadFolderOptions = async (
		inputValue: string
	): Promise<SelectOption[]> => {
		try {
			const response = await apiClient.get<FolderSearchResponse>(
				`/search/folders?q=${encodeURIComponent(inputValue)}&limit=50`
			)
			return response.data.data.map((folder) => ({
				label: folder.name,
				value: folder.id
			}))
		} catch {
			return []
		}
	}

	const loadFeedOptions = async (
		inputValue: string
	): Promise<SelectOption[]> => {
		try {
			const response = await apiClient.get<FeedSearchResponse>(
				`/search/feeds?q=${encodeURIComponent(inputValue)}&limit=50`
			)
			return response.data.data.map((feed) => ({
				label: feed.title,
				value: feed.id
			}))
		} catch {
			return []
		}
	}

	const loadTagOptions = async (
		inputValue: string
	): Promise<SelectOption[]> => {
		try {
			const tags = await searchTags(inputValue, 50)
			return tags.map((tag) => ({
				label: tag.name,
				value: tag.id
			}))
		} catch {
			return []
		}
	}

	const handleApply = () => {
		store.setQ(localQ)
		store.setReadLater(localReadLater)
		store.setFolderOptions(localFolderOptions)
		store.setSubscriptionOptions(localSubscriptionOptions)
		store.setTagOptions(localTagOptions)
		store.setFromDate(localFromDate)
		store.setToDate(localToDate)

		setIsOpen(false)
		router.push('/articles/search')
	}

	const handleReset = (): void => {
		// Clear local state
		setLocalQ('')
		setLocalReadLater('all')
		setLocalFolderOptions([])
		setLocalSubscriptionOptions([])
		setLocalTagOptions([])
		setLocalFromDate('')
		setLocalToDate('')

		store.resetFilters()

		setIsOpen(false)
		router.push('/articles')
	}

	const formContent = (
		<ScrollArea className='max-md:h-40 px-4 md:px-0'>
			<div className='space-y-3'>
				<div className='space-y-2'>
					<Label htmlFor='search'>Search</Label>
					<Input
						id='search'
						onChange={(e) => setLocalQ(e.target.value)}
						placeholder='Search articles...'
						value={localQ}
					/>
				</div>

				<div className='space-y-2'>
					<Label htmlFor='saved'>Saved</Label>
					<Select
						onValueChange={(v) =>
							setLocalReadLater(v as 'all' | 'true' | 'false')
						}
						value={localReadLater}
					>
						<SelectTrigger id='saved'>
							<SelectValue placeholder='All articles' />
						</SelectTrigger>
						<SelectContent>
							<SelectItem value='all'>All articles</SelectItem>
							<SelectItem value='true'>Saved only</SelectItem>
							<SelectItem value='false'>Not saved</SelectItem>
						</SelectContent>
					</Select>
				</div>

				<div className='space-y-2'>
					<Label htmlFor='folder'>Folder</Label>
					<GenericAsyncSelect
						cacheOptions
						inputId='folder'
						isDisabled={false}
						isMulti={true}
						loadOptions={loadFolderOptions}
						onChange={(newValue) =>
							setLocalFolderOptions([...(newValue || [])])
						}
						placeholder='All folders'
						value={localFolderOptions}
					/>
				</div>

				<div className='space-y-2'>
					<Label htmlFor='feed'>Feed</Label>
					<GenericAsyncSelect
						cacheOptions
						inputId='feed'
						isDisabled={false}
						isMulti={true}
						loadOptions={loadFeedOptions}
						onChange={(newValue) =>
							setLocalSubscriptionOptions([...(newValue || [])])
						}
						placeholder='All feeds'
						value={localSubscriptionOptions}
					/>
				</div>

				<div className='space-y-2'>
					<Label htmlFor='tag'>Tag</Label>
					<GenericAsyncSelect
						cacheOptions
						inputId='tag'
						isDisabled={false}
						isMulti={true}
						loadOptions={loadTagOptions}
						onChange={(newValue) => setLocalTagOptions([...(newValue || [])])}
						placeholder='All tags'
						value={localTagOptions}
					/>
				</div>

				<div className='space-y-2'>
					<Label>Date Range</Label>
					<div className='flex flex-col sm:flex-row gap-2'>
						<Input
							onChange={(e) => setLocalFromDate(e.target.value)}
							placeholder='From (YYYY-MM-DD)'
							type='date'
							value={localFromDate}
						/>
						<Input
							onChange={(e) => setLocalToDate(e.target.value)}
							placeholder='To (YYYY-MM-DD)'
							type='date'
							value={localToDate}
						/>
					</div>
				</div>
			</div>
		</ScrollArea>
	)

	return (
		<>
			<Button
				onClick={() => setIsOpen(true)}
				size='sm'
				variant='ghost'
			>
				<IoFilter className='h-4 w-4' />
			</Button>

			{!isMobile && (
				<Dialog
					onOpenChange={setIsOpen}
					open={isOpen}
				>
					<DialogContent className='sm:max-w-md'>
						<DialogHeader>
							<DialogTitle>Filter Articles</DialogTitle>
							<DialogDescription>
								Apply filters to search through articles
							</DialogDescription>
						</DialogHeader>
						{formContent}
						<DialogFooter>
							<Button
								onClick={handleReset}
								type='button'
								variant='outline'
							>
								Reset
							</Button>
							<Button
								onClick={handleApply}
								type='button'
							>
								Apply
							</Button>
						</DialogFooter>
					</DialogContent>
				</Dialog>
			)}

			{isMobile ? (
				<Drawer
					direction='bottom'
					onOpenChange={setIsOpen}
					open={isOpen}
				>
					<DrawerContent>
						<DrawerHeader>
							<DrawerTitle>Filter Articles</DrawerTitle>
							<DrawerDescription>
								Apply filters to search through articles
							</DrawerDescription>
						</DrawerHeader>
						{formContent}
						<DrawerFooter>
							<DrawerClose asChild>
								<Button
									onClick={handleReset}
									type='button'
									variant='outline'
								>
									Reset
								</Button>
							</DrawerClose>
							<Button
								onClick={handleApply}
								type='button'
							>
								Apply
							</Button>
						</DrawerFooter>
					</DrawerContent>
				</Drawer>
			) : null}
		</>
	)
}
