'use client'

import { useRouter } from 'next/navigation'
import { useState } from 'react'
import { toast } from 'sonner'

import { Button } from '@/components/ui/button'
import {
	Dialog,
	DialogContent,
	DialogFooter,
	DialogHeader,
	DialogTitle
} from '@/components/ui/dialog'
import {
	Drawer,
	DrawerClose,
	DrawerContent,
	DrawerFooter,
	DrawerHeader,
	DrawerTitle
} from '@/components/ui/drawer'

import { useRollbackOPML } from '@/hooks/api'
import { useIsMobile } from '@/hooks/ui/media-query'

interface RollbackModalProps {
	importCount: number
	importId: string
	isOpen: boolean
	onOpenChange: (open: boolean) => void
}

export function RollbackModal({
	importCount,
	importId,
	isOpen,
	onOpenChange
}: RollbackModalProps) {
	const router = useRouter()
	const isMobile = useIsMobile()
	const [isSubmitting, setIsSubmitting] = useState(false)
	const rollbackMutation = useRollbackOPML()

	const handleRollback = async () => {
		setIsSubmitting(true)
		try {
			await rollbackMutation.mutate(importId)
			toast.success('Import rolled back successfully')
			onOpenChange(false)
			router.replace('/')
		} catch (error: unknown) {
			console.error('Rollback error:', error)
			const message =
				error instanceof Error ? error.message : 'Failed to rollback import'
			toast.error(message)
		} finally {
			setIsSubmitting(false)
		}
	}

	const handleClose = () => {
		if (!isSubmitting) {
			onOpenChange(false)
		}
	}

	const content = (
		<>
			<div className='text-sm text-muted-foreground/80 px-4 md:px-0'>
				This will permanently delete all {importCount} feeds that were imported
				from this OPML file. This action cannot be undone.
			</div>

			<DialogFooter className='max-md:hidden'>
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
					onClick={handleRollback}
					type='button'
					variant='destructive'
				>
					{isSubmitting ? 'Rolling back...' : 'Rollback Import'}
				</Button>
			</DialogFooter>

			<DrawerFooter className='md:hidden'>
				<DrawerClose asChild>
					<Button
						disabled={isSubmitting}
						type='button'
						variant='outline'
					>
						Cancel
					</Button>
				</DrawerClose>
				<Button
					disabled={isSubmitting}
					onClick={handleRollback}
					type='button'
					variant='destructive'
				>
					{isSubmitting ? 'Rolling back...' : 'Rollback Import'}
				</Button>
			</DrawerFooter>
		</>
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
							<DialogTitle>Rollback Import</DialogTitle>
						</DialogHeader>
						{content}
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
							<DrawerTitle>Rollback Import</DrawerTitle>
						</DrawerHeader>
						{content}
					</DrawerContent>
				</Drawer>
			) : null}
		</>
	)
}
