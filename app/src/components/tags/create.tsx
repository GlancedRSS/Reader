import { useEffect, useRef } from 'react'

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

import { useIsMobile } from '@/hooks/ui/media-query'

interface CreateModalProps {
	isOpen: boolean
	isSaving: boolean
	name: string
	onNameChange: (name: string) => void
	onSave: () => void
	onClose: () => void
}

export function CreateModal({
	isOpen,
	isSaving,
	name,
	onNameChange,
	onSave,
	onClose
}: CreateModalProps) {
	const isMobile = useIsMobile()

	const prevIsOpenRef = useRef<boolean>(false)

	useEffect(() => {
		if (isOpen && !prevIsOpenRef.current) {
			onNameChange('')
		}
		prevIsOpenRef.current = isOpen
	}, [isOpen, onNameChange])

	const formContent = (
		<form onSubmit={(e) => e.preventDefault()}>
			<div className='space-y-4 px-4 md:px-0 md:pb-4'>
				<div className='space-y-2'>
					<Label htmlFor='tag-name'>Name</Label>
					<Input
						disabled={isSaving}
						id='tag-name'
						onChange={(e) => onNameChange(e.target.value)}
						placeholder='Tag name'
						value={name}
					/>
				</div>
			</div>

			<DialogFooter className='max-md:hidden'>
				<Button
					disabled={isSaving}
					onClick={onClose}
					type='button'
					variant='outline'
				>
					Cancel
				</Button>
				<Button
					disabled={!name.trim() || isSaving}
					onClick={onSave}
					type='button'
				>
					{isSaving ? 'Creating...' : 'Create'}
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
					disabled={!name.trim() || isSaving}
					onClick={onSave}
					type='button'
				>
					{isSaving ? 'Creating...' : 'Create'}
				</Button>
			</DrawerFooter>
		</form>
	)

	return (
		<>
			{!isMobile && (
				<Dialog
					onOpenChange={onClose}
					open={isOpen}
				>
					<DialogContent
						className='sm:max-w-md'
						showCloseButton={!isSaving}
					>
						<DialogHeader>
							<DialogTitle>Create tag</DialogTitle>
							<DialogDescription>
								Create a new tag to organize your content
							</DialogDescription>
						</DialogHeader>
						{formContent}
					</DialogContent>
				</Dialog>
			)}

			{isMobile ? (
				<Drawer
					direction='bottom'
					onOpenChange={onClose}
					open={isOpen}
				>
					<DrawerContent>
						<DrawerHeader>
							<DrawerTitle>Create tag</DrawerTitle>
							<DrawerDescription>
								Create a new tag to organize your content
							</DrawerDescription>
						</DrawerHeader>
						{formContent}
					</DrawerContent>
				</Drawer>
			) : null}
		</>
	)
}
