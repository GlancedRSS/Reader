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

import { useIsMobile } from '@/hooks/ui/media-query'

interface DeleteModalProps {
	tagName: string | null
	isDeleting: boolean
	onConfirm: () => void
	onClose: () => void
}

export function DeleteModal({
	tagName,
	isDeleting,
	onConfirm,
	onClose
}: DeleteModalProps) {
	const isMobile = useIsMobile()

	if (!tagName) return null

	const content = (
		<>
			<p className='text-sm text-muted-foreground px-4 md:px-0'>
				Are you sure you want to delete{' '}
				<span className='font-semibold text-foreground'>
					&ldquo;{tagName}&rdquo;
				</span>{' '}
				? This action cannot be undone.
			</p>

			<DialogFooter className='max-md:hidden'>
				<Button
					disabled={isDeleting}
					onClick={onClose}
					type='button'
					variant='outline'
				>
					Cancel
				</Button>
				<Button
					disabled={isDeleting}
					onClick={onConfirm}
					type='button'
					variant='destructive'
				>
					{isDeleting ? 'Deleting...' : 'Delete'}
				</Button>
			</DialogFooter>

			<DrawerFooter className='md:hidden'>
				<DrawerClose asChild>
					<Button
						disabled={isDeleting}
						type='button'
						variant='outline'
					>
						Cancel
					</Button>
				</DrawerClose>
				<Button
					disabled={isDeleting}
					onClick={onConfirm}
					type='button'
					variant='destructive'
				>
					{isDeleting ? 'Deleting...' : 'Delete'}
				</Button>
			</DrawerFooter>
		</>
	)

	return (
		<>
			{!isMobile && (
				<Dialog
					onOpenChange={onClose}
					open={!!tagName}
				>
					<DialogContent
						className='sm:max-w-md'
						showCloseButton={!isDeleting}
					>
						<DialogHeader>
							<DialogTitle>Delete tag</DialogTitle>
							<DialogDescription>
								This action cannot be undone
							</DialogDescription>
						</DialogHeader>
						{content}
					</DialogContent>
				</Dialog>
			)}

			{isMobile ? (
				<Drawer
					direction='bottom'
					onOpenChange={onClose}
					open={!!tagName}
				>
					<DrawerContent>
						<DrawerHeader>
							<DrawerTitle>Delete tag</DrawerTitle>
							<DrawerDescription>
								This action cannot be undone
							</DrawerDescription>
						</DrawerHeader>
						{content}
					</DrawerContent>
				</Drawer>
			) : null}
		</>
	)
}
