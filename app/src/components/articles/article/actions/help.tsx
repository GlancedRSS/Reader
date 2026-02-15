'use client'

import { HelpModal } from '@/components/articles/article/actions/help-modal'
import { forwardRef, useImperativeHandle, useState } from 'react'
import { IoHelpOutline } from 'react-icons/io5'

import { Button } from '@/components/ui/button'
import { Hotkey } from '@/components/ui/hotkey'
import {
	Tooltip,
	TooltipContent,
	TooltipTrigger
} from '@/components/ui/tooltip'

export interface HelpRef {
	trigger: () => void
}

export const Help = forwardRef<HelpRef>((_, ref) => {
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
						<IoHelpOutline className='w-4 h-4' />
					</Button>
				</TooltipTrigger>
				<TooltipContent
					className='flex gap-2'
					sideOffset={4}
				>
					<Hotkey>?</Hotkey>
					<div className='flex items-center'>Keyboard shortcuts</div>
				</TooltipContent>
			</Tooltip>

			<HelpModal
				isOpen={isOpen}
				onOpenChange={setIsOpen}
			/>
		</>
	)
})

Help.displayName = 'Help'
