'use client'

import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { toast } from 'sonner'

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
import { Label } from '@/components/ui/label'
import { Password } from '@/components/ui/password'

import { changePassword } from '@/hooks/api/auth'
import { useIsMobile } from '@/hooks/ui/media-query'

import type { PasswordChangeRequest } from '@/types/api'

interface PasswordChangeModalProps {
	isOpen: boolean
	onOpenChange: (open: boolean) => void
}

export function PasswordChangeModal({
	isOpen,
	onOpenChange
}: PasswordChangeModalProps) {
	const router = useRouter()
	const isMobile = useIsMobile()
	const [currentPassword, setCurrentPassword] = useState('')
	const [newPassword, setNewPassword] = useState('')
	const [isSubmitting, setIsSubmitting] = useState(false)

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault()

		if (!currentPassword.trim() || !newPassword.trim()) {
			toast.error('Please fill in all fields')
			return
		}

		setIsSubmitting(true)

		try {
			const data: PasswordChangeRequest = {
				current_password: currentPassword,
				new_password: newPassword
			}
			const response = await changePassword(data)
			toast.success(response.message)
			router.replace('/sign-in')
			handleClose()
		} catch (error: unknown) {
			console.error('Password change error:', error)
			toast.error(error instanceof Error ? error.message : 'An error occurred')
		} finally {
			setIsSubmitting(false)
		}
	}

	const handleClose = () => {
		if (!isSubmitting) {
			onOpenChange(false)
		}
	}

	useEffect(() => {
		if (isOpen) {
			setCurrentPassword('')
			setNewPassword('')
		}
	}, [isOpen])

	const formContent = (
		<form onSubmit={handleSubmit}>
			<div className='space-y-4 px-4 md:px-0 md:pb-4'>
				<div className='space-y-2'>
					<Label htmlFor='current-password'>Current Password</Label>
					<Password
						autoComplete='current-password'
						disabled={isSubmitting}
						id='current-password'
						onChange={(e) => setCurrentPassword(e.target.value)}
						placeholder='Enter your current password'
						showRequirements={false}
						value={currentPassword}
					/>
				</div>
				<div className='space-y-2'>
					<Label htmlFor='new-password'>New Password</Label>
					<Password
						autoComplete='new-password'
						disabled={isSubmitting}
						id='new-password'
						onChange={(e) => setNewPassword(e.target.value)}
						placeholder='Enter new password'
						showRequirements
						value={newPassword}
					/>
				</div>
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
					disabled={isSubmitting || !currentPassword || !newPassword}
					type='submit'
				>
					{isSubmitting ? 'Updating...' : 'Change Password'}
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
					disabled={isSubmitting || !currentPassword || !newPassword}
					type='submit'
				>
					{isSubmitting ? 'Updating...' : 'Change Password'}
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
							<DialogTitle>Change Password</DialogTitle>
							<DialogDescription>
								Enter your current password and choose a new one. This will sign
								you out from all devices.
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
					open={isOpen}
				>
					<DrawerContent>
						<DrawerHeader>
							<DrawerTitle>Change Password</DrawerTitle>
							<DrawerDescription>
								Enter your current password and choose a new one. This will sign
								you out from all devices.
							</DrawerDescription>
						</DrawerHeader>
						{formContent}
					</DrawerContent>
				</Drawer>
			) : null}
		</>
	)
}
