'use client'

import { useArticlesPaginationStore } from '@/stores/articles-pagination'
import { useLayoutStore } from '@/stores/layout'
import { useParams, useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { toast } from 'sonner'
import { useSWRConfig } from 'swr'

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
import { Switch } from '@/components/ui/switch'

import { useDeleteFeed, useUpdateFeed } from '@/hooks/api/feeds'
import { useIsMobile } from '@/hooks/ui/media-query'

import { apiClient } from '@/lib/api'

import { type UserFeedResponse } from '@/types/api'
import type { SelectOption } from '@/components/ui/async-select'
import type { FolderSearchResponse } from '@/types/api'

interface FeedSettingsModalProps {
	isOpen: boolean
	onOpenChange: (open: boolean) => void
	feed: UserFeedResponse
}

type Step = 'settings' | 'confirm-delete'

export function FeedSettingsModal({
	isOpen,
	onOpenChange,
	feed
}: FeedSettingsModalProps) {
	const params = useParams()
	const feedId = params?.slug as string
	const router = useRouter()
	const isMobile = useIsMobile()
	const { mutate } = useSWRConfig()
	const updateFeed = useUpdateFeed(feedId)
	const deleteFeed = useDeleteFeed(feedId)

	const [step, setStep] = useState<Step>('settings')

	const [title, setTitle] = useState(feed.title)
	const [isPinned, setIsPinned] = useState(feed.is_pinned)
	const [isActive, setIsActive] = useState(feed.is_active)
	const [selectedFolder, setSelectedFolder] = useState<SelectOption | null>(
		null
	)
	const [isSubmitting, setIsSubmitting] = useState(false)

	useEffect(() => {
		setTitle(feed.title)
		setIsPinned(feed.is_pinned)
		setIsActive(feed.is_active)
	}, [feed.title, feed.is_pinned, feed.is_active])

	useEffect(() => {
		if (feed.folder_id) {
			setSelectedFolder({
				label: feed.folder_name || 'Current folder',
				value: feed.folder_id
			})
		} else {
			setSelectedFolder({ label: 'No folder', value: '' })
		}
	}, [feed.folder_id, feed.folder_name])

	useEffect(() => {
		if (isOpen) {
			setStep('settings')
			setTitle(feed.title)
			setIsPinned(feed.is_pinned)
			setIsActive(feed.is_active)
			if (feed.folder_id) {
				setSelectedFolder({
					label: feed.folder_name || 'Current folder',
					value: feed.folder_id
				})
			} else {
				setSelectedFolder({ label: 'No folder', value: '' })
			}
		}
	}, [isOpen, feed])

	const loadFolderOptions = async (
		inputValue: string
	): Promise<SelectOption[]> => {
		try {
			const response = await apiClient.get<FolderSearchResponse>(
				`/search/folders?q=${encodeURIComponent(inputValue)}&limit=50`
			)

			const options: SelectOption[] = [
				{ label: 'No folder', value: '' },
				...response.data.data.map((folder) => ({
					label: folder.name,
					value: folder.id
				}))
			]

			return options
		} catch {
			return [{ label: 'No folder', value: '' }]
		}
	}

	const handleSave = async (e: React.FormEvent) => {
		e.preventDefault()

		if (!title.trim()) {
			toast.error('Please enter a feed title')
			return
		}

		setIsSubmitting(true)

		try {
			await updateFeed.mutate({
				folder_id: selectedFolder?.value || null,
				is_active: isActive,
				is_pinned: isPinned,
				title: title.trim()
			})

			mutate(
				`/feeds/${feedId}`,
				{
					...feed,
					folder_id: selectedFolder?.value || null,
					folder_name: selectedFolder?.value ? selectedFolder.label : null,
					is_active: isActive,
					is_pinned: isPinned,
					title: title.trim()
				},
				false
			)

			mutate('/folders/tree')

			toast.success('Feed updated successfully!')
			handleClose()
		} catch (error) {
			console.error('Feed update error:', error)
			toast.error('Failed to update feed. Please try again.')
		} finally {
			setIsSubmitting(false)
		}
	}

	const handleClose = () => {
		if (!isSubmitting) {
			onOpenChange(false)
		}
	}

	const handleUnsubscribe = async (e?: React.FormEvent) => {
		e?.preventDefault()

		if (step === 'settings') {
			setStep('confirm-delete')
			return
		}

		setIsSubmitting(true)

		try {
			await deleteFeed.mutate()

			mutate('/folders/tree')

			const { reset, resetFilters } = useArticlesPaginationStore.getState()
			reset()
			resetFilters()

			const { setSelectedArticle } = useLayoutStore.getState()
			setSelectedArticle(null)

			toast.success('Feed unsubscribed successfully!')

			router.push('/articles')
		} catch (error) {
			console.error('Feed unsubscribe error:', error)
			toast.error('Failed to unsubscribe. Please try again.')
		} finally {
			setIsSubmitting(false)
		}
	}

	const handleBackToSettings = () => {
		setStep('settings')
	}

	const formContent = (
		<form onSubmit={handleSave}>
			<div className='space-y-4 px-4 md:px-0 md:pb-4'>
				<div className='space-y-2'>
					<Label htmlFor='title'>Title</Label>
					<Input
						disabled={isSubmitting}
						id='title'
						onChange={(e) => setTitle(e.target.value)}
						placeholder='Feed title'
						value={title}
					/>
				</div>

				<div className='space-y-2'>
					<Label htmlFor='folder'>Folder</Label>
					<GenericAsyncSelect
						cacheOptions={true}
						defaultOptions={[{ label: 'No folder', value: '' }]}
						inputId='folder'
						isDisabled={isSubmitting}
						isMulti={false}
						loadOptions={loadFolderOptions}
						onChange={(newValue) => {
							setSelectedFolder(newValue?.[0] || null)
						}}
						placeholder='Search folders...'
						value={selectedFolder ? [selectedFolder] : []}
					/>
				</div>

				<div className='flex items-center justify-between'>
					<Label htmlFor='pin'>Pin to top</Label>
					<Switch
						checked={isPinned}
						disabled={isSubmitting}
						id='pin'
						onCheckedChange={setIsPinned}
					/>
				</div>

				<div className='flex items-center justify-between'>
					<Label htmlFor='pause'>Pause updates</Label>
					<Switch
						checked={!isActive}
						disabled={isSubmitting}
						id='pause'
						onCheckedChange={(checked) => setIsActive(!checked)}
					/>
				</div>
			</div>

			<DialogFooter className='max-md:hidden gap-2'>
				<Button
					disabled={isSubmitting}
					onClick={() => setStep('confirm-delete')}
					type='button'
					variant='destructive'
				>
					Unsubscribe
				</Button>
				<Button
					disabled={isSubmitting}
					onClick={handleClose}
					type='button'
					variant='outline'
				>
					Cancel
				</Button>
				<Button
					disabled={isSubmitting}
					type='submit'
				>
					{isSubmitting ? 'Saving...' : 'Save'}
				</Button>
			</DialogFooter>

			<DrawerFooter className='md:hidden flex-col gap-2'>
				<Button
					className='w-full'
					disabled={isSubmitting}
					onClick={() => setStep('confirm-delete')}
					type='button'
					variant='destructive'
				>
					Unsubscribe
				</Button>
				<DrawerClose asChild>
					<Button
						className='flex-1'
						disabled={isSubmitting}
						type='button'
						variant='outline'
					>
						Cancel
					</Button>
				</DrawerClose>
				<Button
					className='flex-1'
					disabled={isSubmitting}
					type='submit'
				>
					{isSubmitting ? 'Saving...' : 'Save'}
				</Button>
			</DrawerFooter>
		</form>
	)

	const confirmDeleteContent = (
		<form onSubmit={handleUnsubscribe}>
			<div className='space-y-4 px-4 md:px-0 md:pb-4'>
				<p className='text-sm text-muted-foreground'>
					Are you sure you want to unsubscribe from{' '}
					<strong>{feed.title}</strong>? This action cannot be undone.
				</p>
			</div>

			<DialogFooter className='max-md:hidden gap-2'>
				<Button
					disabled={isSubmitting}
					onClick={handleBackToSettings}
					type='button'
					variant='outline'
				>
					Back
				</Button>
				<Button
					disabled={isSubmitting}
					type='submit'
					variant='destructive'
				>
					{isSubmitting ? 'Unsubscribing...' : 'Confirm unsubscribe'}
				</Button>
			</DialogFooter>

			<DrawerFooter className='md:hidden'>
				<Button
					className='w-full'
					disabled={isSubmitting}
					onClick={handleBackToSettings}
					type='button'
					variant='outline'
				>
					Back
				</Button>
				<Button
					className='w-full'
					disabled={isSubmitting}
					type='submit'
					variant='destructive'
				>
					{isSubmitting ? 'Unsubscribing...' : 'Confirm unsubscribe'}
				</Button>
			</DrawerFooter>
		</form>
	)

	return (
		<>
			{!isMobile && (
				<Dialog
					onOpenChange={handleClose}
					open={isOpen}
				>
					<DialogContent
						className='sm:max-w-md'
						showCloseButton={!isSubmitting}
					>
						<DialogHeader>
							<DialogTitle>
								{step === 'confirm-delete' ? 'Unsubscribe' : 'Feed Settings'}
							</DialogTitle>
							<DialogDescription>
								{step === 'confirm-delete'
									? 'This action cannot be undone'
									: 'Customize your feed preferences'}
							</DialogDescription>
						</DialogHeader>
						{step === 'confirm-delete' ? confirmDeleteContent : formContent}
					</DialogContent>
				</Dialog>
			)}

			{isMobile ? (
				<Drawer
					direction='bottom'
					onOpenChange={handleClose}
					open={isOpen}
				>
					<DrawerContent>
						<DrawerHeader>
							<DrawerTitle>
								{step === 'confirm-delete' ? 'Unsubscribe' : 'Feed Settings'}
							</DrawerTitle>
							<DrawerDescription>
								{step === 'confirm-delete'
									? 'This action cannot be undone'
									: 'Customize your feed preferences'}
							</DrawerDescription>
						</DrawerHeader>
						{step === 'confirm-delete' ? confirmDeleteContent : formContent}
					</DrawerContent>
				</Drawer>
			) : null}
		</>
	)
}
