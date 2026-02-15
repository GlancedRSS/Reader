'use client'

import { TagsModal } from '@/components/articles/article/actions/tags-modal'
import { forwardRef, useImperativeHandle, useState } from 'react'
import { IoPricetags } from 'react-icons/io5'

import { Button } from '@/components/ui/button'
import { Hotkey } from '@/components/ui/hotkey'
import {
	Tooltip,
	TooltipContent,
	TooltipTrigger
} from '@/components/ui/tooltip'

import type { TagListResponse } from '@/types/api'

export interface TagsRef {
	trigger: () => void
}

interface TagsProps {
	articleId: string
	articleTags?: TagListResponse[]
}

export const Tags = forwardRef<TagsRef, TagsProps>(
	({ articleId, articleTags = [] }, ref) => {
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
							<IoPricetags className='w-4 h-4' />
						</Button>
					</TooltipTrigger>
					<TooltipContent
						className='flex gap-2'
						sideOffset={4}
					>
						<Hotkey>T</Hotkey>
						<div className='flex items-center'>
							{articleTags.length > 0
								? `Manage tags (${articleTags.length})`
								: 'Manage tags'}
						</div>
					</TooltipContent>
				</Tooltip>

				<TagsModal
					articleId={articleId}
					initialTags={articleTags}
					isOpen={isOpen}
					onOpenChange={setIsOpen}
				/>
			</>
		)
	}
)

Tags.displayName = 'Tags'
