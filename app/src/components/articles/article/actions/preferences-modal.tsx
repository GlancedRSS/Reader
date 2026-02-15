'use client'

import { FontSize } from '@/components/settings/preferences/font-size'
import { FontSpacing } from '@/components/settings/preferences/font-spacing'
import { toast } from 'sonner'
import { useSWRConfig } from 'swr'

import {
	Dialog,
	DialogContent,
	DialogDescription,
	DialogHeader,
	DialogTitle
} from '@/components/ui/dialog'
import {
	Drawer,
	DrawerContent,
	DrawerDescription,
	DrawerHeader,
	DrawerTitle
} from '@/components/ui/drawer'

import { useUserPreferences } from '@/hooks/api'
import { useUpdateUserPreferences } from '@/hooks/api/me'
import { useIsMobile } from '@/hooks/ui/media-query'

import type { PreferencesResponse, PreferencesUpdateRequest } from '@/types/api'

interface PreferencesModalProps {
	isOpen: boolean
	onOpenChange: (open: boolean) => void
}

export function PreferencesModal({
	isOpen,
	onOpenChange
}: PreferencesModalProps) {
	const isMobile = useIsMobile()
	const { data: preferences, isLoading } = useUserPreferences()
	const updatePreferencesMutation = useUpdateUserPreferences()
	const { mutate: swrMutate } = useSWRConfig()

	const handleUpdatePreference = async (
		key: 'font_size' | 'font_spacing',
		value: PreferencesResponse['font_size' | 'font_spacing']
	) => {
		try {
			const update: PreferencesUpdateRequest = {
				[key]: value
			} as PreferencesUpdateRequest
			await updatePreferencesMutation.mutate(update)
			swrMutate('/me/preferences', { ...preferences, [key]: value }, false)
		} catch (error) {
			const errorMessage =
				error instanceof Error ? error.message : 'Failed to update preference'
			toast.error(errorMessage)
		}
	}

	if (isLoading || !preferences) {
		return null
	}

	const content = (
		<>
			<FontSize
				onChange={(value) => handleUpdatePreference('font_size', value)}
				value={preferences.font_size}
			/>
			<FontSpacing
				onChange={(value) => handleUpdatePreference('font_spacing', value)}
				value={preferences.font_spacing}
			/>
		</>
	)

	return (
		<>
			{!isMobile && (
				<Dialog
					onOpenChange={onOpenChange}
					open={isOpen}
				>
					<DialogContent className='sm:max-w-md'>
						<DialogHeader>
							<DialogTitle>Reading Preferences</DialogTitle>
							<DialogDescription>
								Adjust how articles appear for you
							</DialogDescription>
						</DialogHeader>
						<div className='space-y-6 py-4'>{content}</div>
					</DialogContent>
				</Dialog>
			)}

			{isMobile ? (
				<Drawer
					direction='bottom'
					onOpenChange={onOpenChange}
					open={isOpen}
				>
					<DrawerContent>
						<DrawerHeader>
							<DrawerTitle>Reading Preferences</DrawerTitle>
							<DrawerDescription>
								Adjust how articles appear for you
							</DrawerDescription>
						</DrawerHeader>
						<div className='space-y-6 px-4 pb-6'>{content}</div>
					</DrawerContent>
				</Drawer>
			) : null}
		</>
	)
}
