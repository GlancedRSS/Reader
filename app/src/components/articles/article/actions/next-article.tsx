'use client'

import { forwardRef, useImperativeHandle } from 'react'
import { IoChevronForward } from 'react-icons/io5'

import { Button } from '@/components/ui/button'
import { Hotkey } from '@/components/ui/hotkey'
import {
	Tooltip,
	TooltipContent,
	TooltipTrigger
} from '@/components/ui/tooltip'

export interface NextArticleRef {
	trigger: () => void
}

interface NextArticleProps {
	disabled?: boolean
	onNavigate: () => void
}

export const NextArticle = forwardRef<NextArticleRef, NextArticleProps>(
	({ disabled, onNavigate }, ref) => {
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
						<IoChevronForward className='w-4 h-4' />
					</Button>
				</TooltipTrigger>
				<TooltipContent
					className='flex gap-2'
					sideOffset={4}
				>
					<Hotkey>J</Hotkey>
					<span className='text-sm'>Next article</span>
				</TooltipContent>
			</Tooltip>
		)
	}
)

NextArticle.displayName = 'NextArticle'
