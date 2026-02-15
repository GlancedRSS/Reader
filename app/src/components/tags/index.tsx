'use client'

import { CreateModal } from '@/components/tags/create'
import { DeleteModal } from '@/components/tags/delete'
import { EditModal } from '@/components/tags/edit'
import { EmptyState } from '@/components/tags/empty'
import { TagsTable } from '@/components/tags/table'
import { useEffect, useState } from 'react'
import { IoChevronBack, IoChevronForward } from 'react-icons/io5'
import { toast } from 'sonner'
import { useSWRConfig } from 'swr'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import {
	Table,
	TableBody,
	TableCell,
	TableHead,
	TableHeader,
	TableRow
} from '@/components/ui/table'

import { TAGS_PAGE_SIZE } from '@/constants/tags'

import { useCreateTag, useTags } from '@/hooks/api'
import { useTagSearch } from '@/hooks/api/search'

import { apiClient } from '@/lib/api'

import type {
	ResponseMessage,
	TagListResponse,
	TagUpdateRequest
} from '@/types/api'
import type { ApiError } from '@/types/network'

export function Tags() {
	const { mutate: swrMutate } = useSWRConfig()
	const [currentPage, setCurrentPage] = useState(1)
	const [searchQuery, setSearchQuery] = useState('')
	const [debouncedSearchQuery, setDebouncedSearchQuery] = useState('')

	const isSearching = debouncedSearchQuery.length > 0

	useEffect(() => {
		const timer = setTimeout(() => {
			setDebouncedSearchQuery(searchQuery)
		}, 200)
		return () => clearTimeout(timer)
	}, [searchQuery])

	const {
		data: tagsResponse,
		isLoading: isLoadingTags,
		mutate
	} = useTags(
		!isSearching
			? {
					limit: TAGS_PAGE_SIZE,
					offset: (currentPage - 1) * TAGS_PAGE_SIZE
				}
			: undefined
	)

	const {
		data: searchResponse,
		isLoading: isLoadingSearch,
		mutate: mutateSearch
	} = useTagSearch(
		isSearching
			? {
					limit: TAGS_PAGE_SIZE,
					offset: (currentPage - 1) * TAGS_PAGE_SIZE,
					q: debouncedSearchQuery
				}
			: undefined
	)

	const createTagMutation = useCreateTag()

	const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
	const [editingTag, setEditingTag] = useState<TagListResponse | null>(null)
	const [deletingTag, setDeletingTag] = useState<TagListResponse | null>(null)
	const [newTagName, setNewTagName] = useState('')
	const [isSaving, setIsSaving] = useState(false)

	const isLoading = isSearching ? isLoadingSearch : isLoadingTags

	const tags = (isSearching ? searchResponse?.data : tagsResponse?.data) || []
	const totalTags =
		(isSearching
			? searchResponse?.pagination.total
			: tagsResponse?.pagination.total) ?? 0
	const hasMore =
		(isSearching
			? searchResponse?.pagination.has_more
			: tagsResponse?.pagination.has_more) ?? false

	const totalPages = Math.ceil(totalTags / TAGS_PAGE_SIZE) || 1

	const handlePreviousPage = () => {
		setCurrentPage((prev) => Math.max(1, prev - 1))
	}

	const handleNextPage = () => {
		setCurrentPage((prev) => (hasMore ? prev + 1 : prev))
	}

	useEffect(() => {
		setCurrentPage(1)
	}, [debouncedSearchQuery])

	const handleCreateTag = async () => {
		if (!newTagName.trim()) return
		setIsSaving(true)
		try {
			await createTagMutation.mutate({
				name: newTagName.trim()
			})

			await mutate()
			setIsCreateModalOpen(false)
			setNewTagName('')
			toast.success('Tag created')
		} catch (error) {
			console.error('Failed to create tag:', error)
			const errorMessage =
				error && typeof error === 'object' && 'message' in error
					? (error as ApiError).message
					: 'Failed to create tag'
			toast.error(errorMessage)
		} finally {
			setIsSaving(false)
		}
	}

	const handleUpdateTag = async () => {
		if (!editingTag) return
		setIsSaving(true)
		try {
			const response = await apiClient.put<ResponseMessage>(
				`/tags/${editingTag.id}`,
				{
					name: editingTag.name
				} as TagUpdateRequest
			)

			if (response.status === 200) {
				await mutate()
				await swrMutate(`/tags/${editingTag.id}`)
				setEditingTag(null)
				toast.success('Tag updated')
			}
		} catch (error) {
			console.error('Failed to update tag:', error)
			const errorMessage =
				error && typeof error === 'object' && 'message' in error
					? (error as ApiError).message
					: 'Failed to update tag'
			toast.error(errorMessage)
		} finally {
			setIsSaving(false)
		}
	}

	const handleDeleteClick = (tag: TagListResponse) => {
		setDeletingTag(tag)
	}

	const handleConfirmDelete = async () => {
		if (!deletingTag) return
		setIsSaving(true)
		try {
			const response = await apiClient.delete<ResponseMessage>(
				`/tags/${deletingTag.id}`
			)

			if (response.status === 200) {
				await mutate()
				if (isSearching) {
					await mutateSearch()
				}
				setDeletingTag(null)
				toast.success('Tag deleted')
			}
		} catch (error) {
			console.error('Failed to delete tag:', error)
			const errorMessage =
				error && typeof error === 'object' && 'message' in error
					? (error as ApiError).message
					: 'Failed to delete tag'
			toast.error(errorMessage)
		} finally {
			setIsSaving(false)
		}
	}

	const renderData = () => {
		if (!isLoading && totalTags === 0 && !isSearching) {
			return <EmptyState onCreateTag={() => setIsCreateModalOpen(true)} />
		}
		return (
			<div className='px-4'>
				<div className='flex items-center gap-3'>
					<Input
						className='flex-1'
						onChange={(e) => setSearchQuery(e.target.value)}
						placeholder='Search tags...'
						value={searchQuery}
					/>
					<Button onClick={() => setIsCreateModalOpen(true)}>Create</Button>
				</div>

				{isLoading ? (
					<div className='border rounded-xl max-h-[calc(100dvh-3.5rem-4.25rem-2.5rem-0.75rem-3.5rem)] md:max-h-[calc(100dvh-4.25rem-2.5rem-0.75rem-3rem)] overflow-scroll mt-3'>
						<Table>
							<TableHeader className='bg-sidebar-background'>
								<TableRow>
									<TableHead>Name</TableHead>
									<TableHead>Articles</TableHead>
									<TableHead className='text-right'>Actions</TableHead>
								</TableRow>
							</TableHeader>
							<TableBody>
								{Array.from({ length: 20 }).map((_, index) => (
									<TableRow key={index}>
										<TableCell>
											<Skeleton className='h-4 w-24' />
										</TableCell>
										<TableCell>
											<Skeleton className='h-4 w-8' />
										</TableCell>
										<TableCell className='py-1.5 flex justify-end'>
											<Skeleton className='h-8 w-8' />
										</TableCell>
									</TableRow>
								))}
							</TableBody>
						</Table>
					</div>
				) : (
					<>
						<TagsTable
							onDeleteClick={handleDeleteClick}
							onEditTag={setEditingTag}
							tags={tags}
						/>

						{totalTags > 0 && (
							<div className='flex items-center justify-between max-md:justify-end pt-3'>
								<span
									className={`text-sm text-muted-foreground ${totalPages === 1 ? '' : 'max-md:hidden'} `}
								>
									Showing{' '}
									{tags.length > 0 ? (currentPage - 1) * TAGS_PAGE_SIZE + 1 : 0}
									{' - '}
									{(currentPage - 1) * TAGS_PAGE_SIZE + tags.length} of{' '}
									{totalTags} tag{totalTags !== 1 ? 's' : ''}
								</span>
								{totalPages > 1 && (
									<div className='flex items-center gap-2'>
										<span className='text-sm text-muted-foreground'>
											Page {currentPage} of {totalPages}
										</span>
										<div className='flex gap-1'>
											<Button
												className='h-7 sm:h-5'
												disabled={currentPage === 1}
												onClick={handlePreviousPage}
												size='sm'
												type='button'
												variant='ghost'
											>
												<IoChevronBack className='size-4' />
											</Button>
											<Button
												className='h-7 sm:h-5'
												disabled={!hasMore}
												onClick={handleNextPage}
												size='sm'
												type='button'
												variant='ghost'
											>
												<IoChevronForward className='size-4' />
											</Button>
										</div>
									</div>
								)}
							</div>
						)}
					</>
				)}
			</div>
		)
	}

	return (
		<>
			{renderData()}
			<CreateModal
				isOpen={isCreateModalOpen}
				isSaving={isSaving}
				name={newTagName}
				onClose={() => setIsCreateModalOpen(false)}
				onNameChange={setNewTagName}
				onSave={handleCreateTag}
			/>
			<EditModal
				isSaving={isSaving}
				onClose={() => setEditingTag(null)}
				onSave={handleUpdateTag}
				onTagChange={setEditingTag}
				tag={editingTag}
			/>
			<DeleteModal
				isDeleting={isSaving}
				onClose={() => setDeletingTag(null)}
				onConfirm={handleConfirmDelete}
				tagName={deletingTag?.name || null}
			/>
		</>
	)
}
