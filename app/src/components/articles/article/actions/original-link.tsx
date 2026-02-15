'use client'

import { forwardRef, useImperativeHandle } from 'react'
import { IoLink } from 'react-icons/io5'

import { Button } from '@/components/ui/button'
import { Hotkey } from '@/components/ui/hotkey'
import {
	Tooltip,
	TooltipContent,
	TooltipTrigger
} from '@/components/ui/tooltip'

interface OriginalLinkProps {
	link: string | undefined
}

export interface OriginalLinkRef {
	trigger: () => void
}

export const OriginalLink = forwardRef<OriginalLinkRef, OriginalLinkProps>(
	({ link }, ref) => {
		const handleOriginalClick = () => {
			if (link) {
				window.open(link, '_blank', 'noopener,noreferrer')
			}
		}

		useImperativeHandle(ref, () => ({
			trigger: handleOriginalClick
		}))

		return (
			<Tooltip>
				<TooltipTrigger asChild>
					<Button
						className='flex items-center gap-2 px-4 py-2'
						disabled={!link}
						onClick={handleOriginalClick}
						size='icon'
						variant='outline'
					>
						<IoLink className='w-4 h-4' />
					</Button>
				</TooltipTrigger>
				<TooltipContent
					className='flex gap-2'
					sideOffset={4}
				>
					<Hotkey>V</Hotkey>
					<div className='flex items-center'>Open original article</div>
				</TooltipContent>
			</Tooltip>
		)
	}
)

OriginalLink.displayName = 'OriginalLink'
