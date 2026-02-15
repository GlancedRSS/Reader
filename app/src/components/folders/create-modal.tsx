'use client'

import { useLayoutStore } from '@/stores/layout'
import { useEffect, useRef, useState } from 'react'
import { toast } from 'sonner'
import { mutate } from 'swr'

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

import { useCreateFolder } from '@/hooks/api'
import { useIsMobile } from '@/hooks/ui/media-query'

import { apiClient } from '@/lib/api'

import type { SelectOption } from '@/components/ui/async-select'
import type { FolderSearchResponse } from '@/types/api'

export function CreateFolderModal() {
	const isMobile = useIsMobile()
	const createFolder = useCreateFolder()

	const folderModalOpen = useLayoutStore((state) => state.folderModalOpen)
	const defaultParentFolderId = useLayoutStore(
		(state) => state.defaultParentFolderId
	)
	const closeFolderModal = useLayoutStore((state) => state.closeFolderModal)

	const [name, setName] = useState('')
	const [parentId, setParentId] = useState(defaultParentFolderId || '')
	const [selectedFolder, setSelectedFolder] = useState<SelectOption | null>(
		null
	)
	const [isSaving, setIsSaving] = useState(false)

	const handleChange = (newValue: SelectOption | null) => {
		setSelectedFolder(newValue)
		setParentId(newValue?.value || '')
	}

	const prevIsOpenRef = useRef<boolean>(false)
	const prevDefaultParentIdRef = useRef<string | undefined>(
		defaultParentFolderId
	)

	useEffect(() => {
		if (folderModalOpen && !prevIsOpenRef.current) {
			setName('')
			if (
				defaultParentFolderId &&
				defaultParentFolderId !== prevDefaultParentIdRef.current
			) {
				setParentId(defaultParentFolderId)
				setSelectedFolder({
					label: 'Current folder',
					value: defaultParentFolderId
				})
			} else {
				setParentId('')
				setSelectedFolder(null)
			}
			prevDefaultParentIdRef.current = defaultParentFolderId
		}
		prevIsOpenRef.current = folderModalOpen
	}, [folderModalOpen, defaultParentFolderId])

	const handleClose = () => {
		if (!isSaving) {
			closeFolderModal()
		}
	}

	const handleSave = async () => {
		if (!name.trim()) {
			toast.error('Please enter a folder name')
			return
		}

		setIsSaving(true)
		try {
			await createFolder.mutate({
				name: name.trim(),
				...(parentId ? { parent_id: parentId } : {})
			})

			mutate('/folders/tree')

			toast.success('Folder created successfully')
			handleClose()
		} catch (error) {
			console.error('Failed to create folder:', error)
			toast.error(
				error instanceof Error ? error.message : 'Failed to create folder'
			)
		} finally {
			setIsSaving(false)
		}
	}

	const loadFolderOptions = async (
		inputValue: string
	): Promise<SelectOption[]> => {
		try {
			const response = await apiClient.get<FolderSearchResponse>(
				`/search/folders?q=${encodeURIComponent(inputValue)}&limit=20`
			)

			const options: SelectOption[] = [
				{ label: 'Root level', value: '' },
				...response.data.data.map((folder) => ({
					label: folder.name,
					value: folder.id
				}))
			]

			return options
		} catch {
			return [{ label: 'Root level', value: '' }]
		}
	}

	const formContent = (
		<>
			<div className='space-y-4 px-4 md:px-0'>
				<div className='space-y-2'>
					<Label htmlFor='folder-name'>Folder name</Label>
					<Input
						autoFocus
						id='folder-name'
						maxLength={16}
						onChange={(e) => setName(e.target.value)}
						placeholder='e.g., Tech, News, Blogs'
						value={name}
					/>
					<p className='text-xs text-muted-foreground'>
						{name.length}/16 characters
					</p>
				</div>

				<div className='space-y-2'>
					<Label htmlFor='parent-folder'>
						Parent folder{' '}
						<span className='text-muted-foreground'>(optional)</span>
					</Label>
					<GenericAsyncSelect
						cacheOptions={true}
						defaultOptions={[{ label: 'Root level', value: '' }]}
						inputId='parent-folder'
						isDisabled={isSaving}
						isMulti={false}
						loadOptions={loadFolderOptions}
						onChange={(newValue) => {
							const selected = newValue?.[0]
							handleChange(selected || null)
						}}
						placeholder='Search folders...'
						value={selectedFolder ? [selectedFolder] : []}
					/>
				</div>
			</div>

			<DialogFooter className='max-md:hidden'>
				<Button
					disabled={isSaving}
					onClick={handleClose}
					type='button'
					variant='outline'
				>
					Cancel
				</Button>
				<Button
					disabled={isSaving || !name.trim()}
					onClick={handleSave}
					type='button'
				>
					{isSaving ? 'Creating...' : 'Create folder'}
				</Button>
			</DialogFooter>

			<DrawerFooter className='md:hidden'>
				<DrawerClose asChild>
					<Button
						disabled={isSaving}
						type='button'
						variant='outline'
					>
						Cancel
					</Button>
				</DrawerClose>
				<Button
					disabled={isSaving || !name.trim()}
					onClick={handleSave}
					type='button'
				>
					{isSaving ? 'Creating...' : 'Create folder'}
				</Button>
			</DrawerFooter>
		</>
	)

	return (
		<>
			{!isMobile && (
				<Dialog
					onOpenChange={handleClose}
					open={folderModalOpen}
				>
					<DialogContent
						className='sm:max-w-md'
						showCloseButton={!isSaving}
					>
						<DialogHeader>
							<DialogTitle>New folder</DialogTitle>
							<DialogDescription>
								Create a folder to organize your feeds
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
					open={folderModalOpen}
				>
					<DrawerContent>
						<DrawerHeader>
							<DrawerTitle>New folder</DrawerTitle>
							<DrawerDescription>
								Create a folder to organize your feeds
							</DrawerDescription>
						</DrawerHeader>
						{formContent}
					</DrawerContent>
				</Drawer>
			) : null}
		</>
	)
}
