'use client'

import { forwardRef, useImperativeHandle } from 'react'
import { IoChevronBack } from 'react-icons/io5'

import { Button } from '@/components/ui/button'
import { Hotkey } from '@/components/ui/hotkey'
import {
	Tooltip,
	TooltipContent,
	TooltipTrigger
} from '@/components/ui/tooltip'

export interface PreviousArticleRef {
	trigger: () => void
}

interface PreviousArticleProps {
	disabled?: boolean
	onNavigate: () => void
}

export const PreviousArticle = forwardRef<
	PreviousArticleRef,
	PreviousArticleProps
>(({ disabled, onNavigate }, ref) => {
	const handleNavigate = () => {
		if (!disabled) {
			onNavigate()
		}
	}

	useImperativeHandle(ref, () => ({
		trigger: handleNavigate
	}))

	return (
		<Tooltip>
			<TooltipTrigger asChild>
				<Button
					className='flex items-center gap-2 px-4 py-2'
					disabled={disabled}
					onClick={handleNavigate}
					size='icon'
					variant='outline'
				>
					<IoChevronBack className='w-4 h-4' />
				</Button>
			</TooltipTrigger>
			<TooltipContent
				className='flex gap-2'
				sideOffset={4}
			>
				<Hotkey>K</Hotkey>
				<span className='text-sm'>Previous article</span>
			</TooltipContent>
		</Tooltip>
	)
})

PreviousArticle.displayName = 'PreviousArticle'
