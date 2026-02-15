'use client'

import { useLayoutStore } from '@/stores/layout'
import { useCallback, useEffect, useState } from 'react'

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
	DrawerContent,
	DrawerDescription,
	DrawerFooter,
	DrawerHeader,
	DrawerTitle
} from '@/components/ui/drawer'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue
} from '@/components/ui/select'

import { useDiscoveryFlow } from '@/hooks/features/discovery'
import { useIsMobile } from '@/hooks/ui/media-query'

import { apiClient } from '@/lib/api'

import type { SelectOption } from '@/components/ui/async-select'
import type { FolderSearchResponse } from '@/types/api'

export function DiscoveryModal() {
	const isMobile = useIsMobile()
	const { discoveryModalOpen, closeDiscoveryModal } = useLayoutStore()

	const [selectedFolder, setSelectedFolder] = useState<SelectOption | null>(
		null
	)
	const [folderId, setFolderId] = useState('')

	const discovery = useDiscoveryFlow(
		folderId
			? {
					folderId,
					onSuccess: closeDiscoveryModal
				}
			: {
					onSuccess: closeDiscoveryModal
				}
	)

	const handleClose = useCallback(() => {
		closeDiscoveryModal()
	}, [closeDiscoveryModal])

	const handleFolderChange = useCallback((newValue: SelectOption | null) => {
		setSelectedFolder(newValue)
		setFolderId(newValue?.value || '')
	}, [])

	const loadFolderOptions = useCallback(
		async (inputValue: string): Promise<SelectOption[]> => {
			try {
				const response = await apiClient.get<FolderSearchResponse>(
					`/search/folders?q=${encodeURIComponent(inputValue)}&limit=20`
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
		},
		[]
	)

	useEffect(() => {
		if (discoveryModalOpen) {
			discovery.resetToInitial()
			setSelectedFolder(null)
			setFolderId('')
		}
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, [discoveryModalOpen, discovery.resetToInitial])

	const formContent = (
		<>
			<div className='space-y-4 px-4 md:px-0'>
				{discovery.showSelect ? (
					<Select
						disabled={discovery.isSubscribing}
						onValueChange={discovery.setSelectedFeedUrl}
						value={discovery.selectedFeedUrl}
					>
						<SelectTrigger>
							<SelectValue placeholder='Select a feed' />
						</SelectTrigger>
						<SelectContent
							align='start'
							className='w-(--radix-select-trigger-width)'
						>
							{discovery.feeds.map((feedUrl) => (
								<SelectItem
									key={feedUrl}
									value={feedUrl}
								>
									{feedUrl}
								</SelectItem>
							))}
						</SelectContent>
					</Select>
				) : (
					<>
						<Input
							disabled={discovery.isDiscovering}
							onChange={(e) => discovery.setUrl(e.target.value)}
							placeholder='https://example.com/feed.xml'
							type='url'
							value={discovery.url}
						/>
						<input
							accept='.opml'
							disabled={discovery.isImporting}
							hidden
							onChange={discovery.handleOpmlImport}
							ref={discovery.fileInputRef}
							type='file'
						/>
					</>
				)}

				<div className='space-y-2'>
					<Label htmlFor='folder'>
						Folder <span className='text-muted-foreground'>(optional)</span>
					</Label>
					<GenericAsyncSelect
						cacheOptions={true}
						defaultOptions={[{ label: 'No folder', value: '' }]}
						inputId='folder'
						isDisabled={
							discovery.isDiscovering ||
							discovery.isSubscribing ||
							discovery.isImporting
						}
						isMulti={false}
						loadOptions={loadFolderOptions}
						onChange={(newValue) => {
							const selected = newValue?.[0]
							handleFolderChange(selected || null)
						}}
						placeholder='Search folders...'
						value={selectedFolder ? [selectedFolder] : []}
					/>
				</div>
			</div>

			<DialogFooter className='max-md:hidden'>
				{discovery.showSelect ? (
					<>
						<Button
							disabled={discovery.isSubscribing}
							onClick={discovery.resetToInitial}
							type='button'
							variant='outline'
						>
							Back
						</Button>
						<Button
							disabled={discovery.isSubscribing || !discovery.selectedFeedUrl}
							onClick={discovery.handleSubscribe}
							type='button'
						>
							{discovery.isSubscribing ? 'Subscribing...' : 'Subscribe'}
						</Button>
					</>
				) : (
					<>
						<Button
							disabled={discovery.isImporting || discovery.isDiscovering}
							onClick={() => discovery.fileInputRef.current?.click()}
							type='button'
							variant='outline'
						>
							{discovery.isImporting ? 'Importing...' : 'Import OPML'}
						</Button>
						<Button
							disabled={discovery.isDiscovering || !discovery.url.trim()}
							onClick={discovery.handleDiscoverFeeds}
							type='button'
						>
							{discovery.isDiscovering ? 'Subscribing...' : 'Subscribe'}
						</Button>
					</>
				)}
			</DialogFooter>

			<DrawerFooter className='md:hidden'>
				{discovery.showSelect ? (
					<>
						<Button
							disabled={discovery.isSubscribing}
							onClick={discovery.resetToInitial}
							type='button'
							variant='outline'
						>
							Back
						</Button>
						<Button
							disabled={discovery.isSubscribing || !discovery.selectedFeedUrl}
							onClick={discovery.handleSubscribe}
							type='button'
						>
							{discovery.isSubscribing ? 'Subscribing...' : 'Subscribe'}
						</Button>
					</>
				) : (
					<>
						<Button
							disabled={discovery.isImporting || discovery.isDiscovering}
							onClick={() => discovery.fileInputRef.current?.click()}
							type='button'
							variant='outline'
						>
							{discovery.isImporting ? 'Importing...' : 'Import OPML'}
						</Button>
						<Button
							disabled={discovery.isDiscovering || !discovery.url.trim()}
							onClick={discovery.handleDiscoverFeeds}
							type='button'
						>
							{discovery.isDiscovering ? 'Subscribing...' : 'Subscribe'}
						</Button>
					</>
				)}
			</DrawerFooter>
		</>
	)

	return (
		<>
			{!isMobile && (
				<Dialog
					onOpenChange={handleClose}
					open={discoveryModalOpen}
				>
					<DialogContent className='sm:max-w-md'>
						<DialogHeader>
							<DialogTitle>Add Feed</DialogTitle>
							<DialogDescription>
								Subscribe to a new feed via URL or import from OPML.
							</DialogDescription>
						</DialogHeader>
						{formContent}
					</DialogContent>
				</Dialog>
			)}

			{isMobile ? (
				<Drawer
					direction='bottom'
					onOpenChange={handleClose}
					open={discoveryModalOpen}
				>
					<DrawerContent>
						<DrawerHeader>
							<DrawerTitle>Add Feed</DrawerTitle>
							<DrawerDescription>
								Subscribe to a new feed via URL or import from OPML.
							</DrawerDescription>
						</DrawerHeader>
						{formContent}
					</DrawerContent>
				</Drawer>
			) : null}
		</>
	)
}
