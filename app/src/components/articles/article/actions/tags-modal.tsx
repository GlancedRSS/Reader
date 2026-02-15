'use client'

import { useEffect, useState } from 'react'
import { toast } from 'sonner'
import { useSWRConfig } from 'swr'

import { GenericAsyncSelect } from '@/components/ui/async-select'
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

import { useUpdateArticleState } from '@/hooks/api'
import { searchTags } from '@/hooks/api/tags'
import { useIsMobile } from '@/hooks/ui/media-query'

import type { SelectOption } from '@/components/ui/async-select'
import type { ArticleStateUpdateRequest, TagListResponse } from '@/types/api'

interface TagsModalProps {
	articleId: string
	initialTags?: TagListResponse[]
	isOpen: boolean
	onOpenChange: (open: boolean) => void
}

export function TagsModal({
	articleId,
	initialTags = [],
	isOpen,
	onOpenChange
}: TagsModalProps) {
	const isMobile = useIsMobile()
	const updateArticleState = useUpdateArticleState(articleId)
	const { mutate: swrMutate, cache } = useSWRConfig()
	const [selectedTags, setSelectedTags] = useState<SelectOption[]>([])
	const [isSaving, setIsSaving] = useState(false)

	useEffect(() => {
		if (isOpen) {
			const tagOptions: SelectOption[] = initialTags.map((tag) => ({
				label: tag.name,
				value: tag.id
			}))
			setSelectedTags(tagOptions)
		} else {
			setSelectedTags([])
		}
	}, [isOpen, initialTags])

	const handleOpenChange = (open: boolean) => {
		onOpenChange(open)
	}

	const handleSave = async () => {
		setIsSaving(true)
		try {
			const update: ArticleStateUpdateRequest = {
				tag_ids: selectedTags.map((t) => t.value)
			}
			await updateArticleState.mutate(update)
			const articleKey = `/articles/${articleId}`
			const currentArticle = cache.get(articleKey)
			if (currentArticle?.data) {
				const newTags: TagListResponse[] = selectedTags.map((tag) => ({
					article_count: 0,
					id: tag.value,
					name: tag.label
				}))
				await swrMutate(
					articleKey,
					{ ...currentArticle.data, tags: newTags },
					false
				)
			} else {
				await swrMutate(articleKey)
			}
			toast.success('Tags updated')
			handleOpenChange(false)
		} catch (error) {
			const errorMessage =
				error instanceof Error ? error.message : 'Failed to update tags'
			toast.error(errorMessage)
		} finally {
			setIsSaving(false)
		}
	}

	const handleClose = () => {
		if (!isSaving) {
			handleOpenChange(false)
		}
	}

	const loadTagOptions = async (inputValue: string) => {
		try {
			const tags = await searchTags(inputValue, 50)
			return tags.map((tag) => ({
				label: tag.name,
				value: tag.id
			}))
		} catch (error) {
			console.error('Failed to load tags:', error)
			return []
		}
	}

	const content = (
		<>
			<div className='space-y-4 px-4 md:px-0'>
				<div className='space-y-2'>
					<div className='flex justify-between'>
						<Label htmlFor='tags-search'>Search and select tags</Label>
						<p className='text-xs text-muted-foreground'>
							{`${selectedTags.length} tag${selectedTags.length === 1 ? '' : 's'} selected`}
						</p>
					</div>
					<GenericAsyncSelect
						inputId='tags-search'
						isDisabled={isSaving}
						loadOptions={loadTagOptions}
						loadingMessage={() => 'Loading tags...'}
						noOptionsMessage={({ inputValue }) =>
							inputValue ? 'No tags found' : 'Start typing to search...'
						}
						onChange={(newValue) => setSelectedTags([...(newValue ?? [])])}
						placeholder='Type to search tags...'
						value={selectedTags}
					/>
				</div>
			</div>

			<DialogFooter className='max-md:hidden'>
				<Button
					disabled={isSaving}
					onClick={handleClose}
					type='button'
					variant='outline'
				>
					Cancel
				</Button>
				<Button
					disabled={isSaving}
					onClick={handleSave}
					type='button'
				>
					{isSaving ? 'Saving...' : 'Save'}
				</Button>
			</DialogFooter>

			<DrawerFooter className='md:hidden'>
				<DrawerClose asChild>
					<Button
						disabled={isSaving}
						type='button'
						variant='outline'
					>
						Cancel
					</Button>
				</DrawerClose>
				<Button
					disabled={isSaving}
					onClick={handleSave}
					type='button'
				>
					{isSaving ? 'Saving...' : 'Save'}
				</Button>
			</DrawerFooter>
		</>
	)

	return (
		<>
			{!isMobile && (
				<Dialog
					onOpenChange={handleOpenChange}
					open={isOpen}
				>
					<DialogContent
						className='sm:max-w-md'
						showCloseButton={!isSaving}
					>
						<DialogHeader>
							<DialogTitle>Manage Tags</DialogTitle>
							<DialogDescription>
								Search and select tags to assign to this article
							</DialogDescription>
						</DialogHeader>
						{content}
					</DialogContent>
				</Dialog>
			)}

			{isMobile ? (
				<Drawer
					direction='bottom'
					onOpenChange={handleOpenChange}
					open={isOpen}
				>
					<DrawerContent>
						<DrawerHeader>
							<DrawerTitle>Manage Tags</DrawerTitle>
							<DrawerDescription>
								Search and select tags to assign to this article
							</DrawerDescription>
						</DrawerHeader>
						{content}
					</DrawerContent>
				</Drawer>
			) : null}
		</>
	)
}
