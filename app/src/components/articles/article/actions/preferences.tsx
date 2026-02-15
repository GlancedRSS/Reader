'use client'

import { PreferencesModal } from '@/components/articles/article/actions/preferences-modal'
import { forwardRef, useImperativeHandle, useState } from 'react'
import { IoSettingsOutline } from 'react-icons/io5'

import { Button } from '@/components/ui/button'
import { Hotkey } from '@/components/ui/hotkey'
import {
	Tooltip,
	TooltipContent,
	TooltipTrigger
} from '@/components/ui/tooltip'

export interface PreferencesRef {
	trigger: () => void
}

export const Preferences = forwardRef<PreferencesRef>((_, ref) => {
	const [isOpen, setIsOpen] = useState(false)

	useImperativeHandle(ref, () => ({
		trigger: () => setIsOpen(true)
	}))

	return (
		<>
			<Tooltip>
				<TooltipTrigger asChild>
					<Button
						className='flex items-center gap-2 px-4 py-2'
						onClick={() => setIsOpen(true)}
						size='icon'
						variant='outline'
					>
						<IoSettingsOutline className='w-4 h-4' />
					</Button>
				</TooltipTrigger>
				<TooltipContent
					className='flex gap-2'
					sideOffset={4}
				>
					<Hotkey>P</Hotkey>
					<div className='flex items-center'>Preferences</div>
				</TooltipContent>
			</Tooltip>

			<PreferencesModal
				isOpen={isOpen}
				onOpenChange={setIsOpen}
			/>
		</>
	)
})

Preferences.displayName = 'Preferences'
