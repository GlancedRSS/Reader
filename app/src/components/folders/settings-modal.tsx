'use client'

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

import { useDeleteFolder, useUpdateFolder } from '@/hooks/api/folders'
import { useIsMobile } from '@/hooks/ui/media-query'

import { apiClient } from '@/lib/api'

import type { SelectOption } from '@/components/ui/async-select'
import type { FolderListResponse, FolderSearchResponse } from '@/types/api'

interface FolderSettingsModalProps {
	isOpen: boolean
	onOpenChange: (open: boolean) => void
	folder: FolderListResponse
}

type Step = 'settings' | 'confirm-delete'

export function FolderSettingsModal({
	isOpen,
	onOpenChange,
	folder
}: FolderSettingsModalProps) {
	const params = useParams()
	const folderId = params?.slug as string
	const router = useRouter()
	const isMobile = useIsMobile()
	const { mutate } = useSWRConfig()
	const updateFolder = useUpdateFolder(folderId)
	const deleteFolder = useDeleteFolder(folderId)

	const [step, setStep] = useState<Step>('settings')

	const [name, setName] = useState(folder.name)
	const [isPinned, setIsPinned] = useState(folder.is_pinned)
	const [selectedParentFolder, setSelectedParentFolder] =
		useState<SelectOption | null>(null)
	const [isSubmitting, setIsSubmitting] = useState(false)

	useEffect(() => {
		setName(folder.name)
		setIsPinned(folder.is_pinned)
	}, [folder.name, folder.is_pinned])

	useEffect(() => {
		if (folder.parent_id) {
			setSelectedParentFolder({
				label: 'Current parent',
				value: folder.parent_id
			})
		} else {
			setSelectedParentFolder({ label: 'No parent', value: '' })
		}
	}, [folder.parent_id])

	useEffect(() => {
		if (isOpen) {
			setStep('settings')
			setName(folder.name)
			setIsPinned(folder.is_pinned)
			if (folder.parent_id) {
				setSelectedParentFolder({
					label: 'Current parent',
					value: folder.parent_id
				})
			} else {
				setSelectedParentFolder({ label: 'No parent', value: '' })
			}
		}
	}, [isOpen, folder])

	const loadFolderOptions = async (
		inputValue: string
	): Promise<SelectOption[]> => {
		try {
			const response = await apiClient.get<FolderSearchResponse>(
				`/search/folders?q=${encodeURIComponent(inputValue)}&limit=50`
			)

			const options: SelectOption[] = [
				{ label: 'No parent', value: '' },
				...response.data.data
					.filter((f) => f.id !== folderId)
					.map((f) => ({
						label: f.name,
						value: f.id
					}))
			]

			return options
		} catch {
			return [{ label: 'No parent', value: '' }]
		}
	}

	const handleSave = async (e: React.FormEvent) => {
		e.preventDefault()

		if (!name.trim()) {
			toast.error('Please enter a folder name')
			return
		}

		setIsSubmitting(true)

		try {
			await updateFolder.mutate({
				is_pinned: isPinned,
				name: name.trim(),
				...(selectedParentFolder?.value
					? { parent_id: selectedParentFolder.value }
					: {})
			})

			mutate(
				`/folders/${folderId}`,
				{
					...folder,
					is_pinned: isPinned,
					name: name.trim(),
					...(selectedParentFolder?.value
						? { parent_id: selectedParentFolder.value }
						: {})
				},
				false
			)

			mutate('/folders/tree')

			toast.success('Folder updated successfully!')
			handleClose()
		} catch (error) {
			console.error('Folder update error:', error)
			toast.error('Failed to update folder. Please try again.')
		} finally {
			setIsSubmitting(false)
		}
	}

	const handleClose = () => {
		if (!isSubmitting) {
			onOpenChange(false)
		}
	}

	const handleDelete = async (e?: React.FormEvent) => {
		e?.preventDefault()

		if (step === 'settings') {
			setStep('confirm-delete')
			return
		}

		setIsSubmitting(true)

		try {
			await deleteFolder.mutate()

			mutate('/folders/tree')

			toast.success('Folder deleted successfully!')
			router.push('/articles')
		} catch (error) {
			console.error('Folder delete error:', error)
			toast.error('Failed to delete folder. Please try again.')
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
					<Label htmlFor='name'>Name</Label>
					<Input
						disabled={isSubmitting}
						id='name'
						onChange={(e) => setName(e.target.value)}
						placeholder='Folder name'
						value={name}
					/>
				</div>

				<div className='space-y-2'>
					<Label htmlFor='parent'>Parent folder</Label>
					<GenericAsyncSelect
						cacheOptions={true}
						defaultOptions={[{ label: 'No parent', value: '' }]}
						inputId='parent'
						isDisabled={isSubmitting}
						isMulti={false}
						loadOptions={loadFolderOptions}
						onChange={(newValue) => {
							setSelectedParentFolder(newValue?.[0] || null)
						}}
						placeholder='Search folders...'
						value={selectedParentFolder ? [selectedParentFolder] : []}
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
			</div>

			<DialogFooter className='max-md:hidden gap-2'>
				<Button
					disabled={isSubmitting}
					onClick={() => setStep('confirm-delete')}
					type='button'
					variant='destructive'
				>
					Delete
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
					Delete
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
		<form onSubmit={handleDelete}>
			<div className='space-y-4 px-4 md:px-0 md:pb-4'>
				<p className='text-sm text-muted-foreground'>
					Are you sure you want to delete <strong>{folder.name}</strong>? This
					action cannot be undone.
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
					{isSubmitting ? 'Deleting...' : 'Confirm delete'}
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
					{isSubmitting ? 'Deleting...' : 'Confirm delete'}
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
								{step === 'confirm-delete' ? 'Delete' : 'Folder Settings'}
							</DialogTitle>
							<DialogDescription>
								{step === 'confirm-delete'
									? 'This action cannot be undone'
									: 'Customize your folder preferences'}
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
								{step === 'confirm-delete' ? 'Delete' : 'Folder Settings'}
							</DrawerTitle>
							<DrawerDescription>
								{step === 'confirm-delete'
									? 'This action cannot be undone'
									: 'Customize your folder preferences'}
							</DrawerDescription>
						</DrawerHeader>
						{step === 'confirm-delete' ? confirmDeleteContent : formContent}
					</DrawerContent>
				</Drawer>
			) : null}
		</>
	)
}
