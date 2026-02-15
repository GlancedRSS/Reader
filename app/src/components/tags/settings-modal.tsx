'use client'

import { useParams, useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { toast } from 'sonner'
import { useSWRConfig } from 'swr'

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

import { useDeleteTag, useUpdateTag } from '@/hooks/api/tags'
import { useIsMobile } from '@/hooks/ui/media-query'

import type { TagListResponse } from '@/types/api'

interface TagSettingsModalProps {
	isOpen: boolean
	onOpenChange: (open: boolean) => void
	tag: TagListResponse
}

type Step = 'settings' | 'confirm-delete'

export function TagSettingsModal({
	isOpen,
	onOpenChange,
	tag
}: TagSettingsModalProps) {
	const params = useParams()
	const tagId = params?.slug as string
	const router = useRouter()
	const { mutate: swrMutate } = useSWRConfig()
	const isMobile = useIsMobile()
	const updateTag = useUpdateTag(tagId)
	const deleteTag = useDeleteTag(tagId)

	const [step, setStep] = useState<Step>('settings')

	const [name, setName] = useState(tag.name)
	const [isSubmitting, setIsSubmitting] = useState(false)

	useEffect(() => {
		setName(tag.name)
	}, [tag.name])

	useEffect(() => {
		if (isOpen) {
			setStep('settings')
			setName(tag.name)
		}
	}, [isOpen, tag])

	const handleSave = async (e: React.FormEvent) => {
		e.preventDefault()

		if (!name.trim()) {
			toast.error('Please enter a tag name')
			return
		}

		setIsSubmitting(true)

		try {
			await updateTag.mutate({
				name: name.trim()
			})

			await swrMutate(`/tags/${tagId}`, { ...tag, name: name.trim() }, false)

			toast.success('Tag updated successfully!')
			handleClose()
		} catch (error) {
			console.error('Tag update error:', error)
			toast.error('Failed to update tag. Please try again.')
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
			await deleteTag.mutate()

			toast.success('Tag deleted successfully!')
			router.push('/articles')
		} catch (error) {
			console.error('Tag delete error:', error)
			toast.error('Failed to delete tag. Please try again.')
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
						placeholder='Tag name'
						value={name}
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
					Are you sure you want to delete <strong>{tag.name}</strong>? This
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
								{step === 'confirm-delete' ? 'Delete' : 'Tag Settings'}
							</DialogTitle>
							<DialogDescription>
								{step === 'confirm-delete'
									? 'This action cannot be undone'
									: 'Customize your tag preferences'}
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
								{step === 'confirm-delete' ? 'Delete' : 'Tag Settings'}
							</DrawerTitle>
							<DrawerDescription>
								{step === 'confirm-delete'
									? 'This action cannot be undone'
									: 'Customize your tag preferences'}
							</DrawerDescription>
						</DrawerHeader>
						{step === 'confirm-delete' ? confirmDeleteContent : formContent}
					</DrawerContent>
				</Drawer>
			) : null}
		</>
	)
}
