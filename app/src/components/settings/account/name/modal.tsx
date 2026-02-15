'use client'

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
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

import { useMe, useUpdateProfile } from '@/hooks/api/me'
import { useIsMobile } from '@/hooks/ui/media-query'

import type { ProfileUpdateRequest } from '@/types/api'

interface NameChangeModalProps {
	isOpen: boolean
	onOpenChange: (open: boolean) => void
}

interface NameFormData {
	firstName: string
	lastName: string
}

export function NameChangeModal({
	isOpen,
	onOpenChange
}: NameChangeModalProps) {
	const { data: user, mutate: refreshUser } = useMe()
	const { mutate: updateProfileMutation } = useUpdateProfile()
	const isMobile = useIsMobile()
	const [formData, setFormData] = useState<NameFormData>({
		firstName: user?.first_name || '',
		lastName: user?.last_name || ''
	})

	const updateFormData = (field: keyof NameFormData, value: string) => {
		setFormData((prev) => ({ ...prev, [field]: value }))
	}

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault()
		try {
			const data: ProfileUpdateRequest = {}
			if (formData.firstName) data.first_name = formData.firstName
			if (formData.lastName) data.last_name = formData.lastName
			await updateProfileMutation(data)
			await refreshUser()
			toast.success('Profile updated successfully')
			onOpenChange(false)
		} catch {
			// Error handled by SWR/api layer
		}
	}

	const handleClose = () => {
		setFormData({
			firstName: user?.first_name || '',
			lastName: user?.last_name || ''
		})
		onOpenChange(false)
	}

	// Reset form when user data changes or modal opens
	useEffect(() => {
		if (isOpen) {
			setFormData({
				firstName: user?.first_name || '',
				lastName: user?.last_name || ''
			})
		}
	}, [isOpen, user])

	const formContent = (
		<form onSubmit={handleSubmit}>
			<div className='space-y-4 px-4 md:px-0 md:pb-4'>
				<div className='space-y-2'>
					<Label htmlFor='first-name'>First Name</Label>
					<Input
						autoComplete='given-name'
						id='first-name'
						onChange={(e) => updateFormData('firstName', e.target.value)}
						placeholder='Enter your first name'
						value={formData.firstName}
					/>
				</div>

				<div className='space-y-2'>
					<Label htmlFor='last-name'>Last Name</Label>
					<Input
						autoComplete='family-name'
						id='last-name'
						onChange={(e) => updateFormData('lastName', e.target.value)}
						placeholder='Enter your last name'
						value={formData.lastName}
					/>
				</div>
			</div>

			<DialogFooter className='max-md:hidden'>
				<Button
					onClick={handleClose}
					type='button'
					variant='outline'
				>
					Cancel
				</Button>
				<Button type='submit'>Save Changes</Button>
			</DialogFooter>

			<DrawerFooter className='md:hidden'>
				<DrawerClose asChild>
					<Button
						type='button'
						variant='outline'
					>
						Cancel
					</Button>
				</DrawerClose>
				<Button type='submit'>Save Changes</Button>
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
					<DialogContent className='sm:max-w-md'>
						<DialogHeader>
							<DialogTitle>Change Name</DialogTitle>
							<DialogDescription>
								Enter your first and last name. This is shown in your profile.
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
							<DrawerTitle>Change Name</DrawerTitle>
							<DrawerDescription>
								Enter your first and last name. This is shown in your profile.
							</DrawerDescription>
						</DrawerHeader>
						{formContent}
					</DrawerContent>
				</Drawer>
			) : null}
		</>
	)
}
