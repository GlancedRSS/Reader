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

import type { TagListResponse } from '@/types/api'

interface EditModalProps {
	tag: TagListResponse | null
	isSaving: boolean
	onTagChange: (tag: TagListResponse) => void
	onSave: () => void
	onClose: () => void
}

export function EditModal({
	tag,
	isSaving,
	onTagChange,
	onSave,
	onClose
}: EditModalProps) {
	const isMobile = useIsMobile()

	if (!tag) return null

	const formContent = (
		<form onSubmit={(e) => e.preventDefault()}>
			<div className='space-y-4 px-4 md:px-0 md:pb-4'>
				<div className='space-y-2'>
					<Label htmlFor='tag-name-edit'>Name</Label>
					<Input
						disabled={isSaving}
						id='tag-name-edit'
						onChange={(e) => onTagChange({ ...tag, name: e.target.value })}
						placeholder='Tag name'
						value={tag.name}
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
					disabled={!tag.name.trim() || isSaving}
					onClick={onSave}
					type='button'
				>
					{isSaving ? 'Saving...' : 'Save'}
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
					disabled={!tag.name.trim() || isSaving}
					onClick={onSave}
					type='button'
				>
					{isSaving ? 'Saving...' : 'Save'}
				</Button>
			</DrawerFooter>
		</form>
	)

	return (
		<>
			{!isMobile && (
				<Dialog
					onOpenChange={onClose}
					open={!!tag}
				>
					<DialogContent
						className='sm:max-w-md'
						showCloseButton={!isSaving}
					>
						<DialogHeader>
							<DialogTitle>Edit tag</DialogTitle>
							<DialogDescription>Modify tag name</DialogDescription>
						</DialogHeader>
						{formContent}
					</DialogContent>
				</Dialog>
			)}

			{isMobile ? (
				<Drawer
					direction='bottom'
					onOpenChange={onClose}
					open={!!tag}
				>
					<DrawerContent>
						<DrawerHeader>
							<DrawerTitle>Edit tag</DrawerTitle>
							<DrawerDescription>Modify tag name</DrawerDescription>
						</DrawerHeader>
						{formContent}
					</DrawerContent>
				</Drawer>
			) : null}
		</>
	)
}
