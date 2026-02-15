'use client'

import { SearchLoading } from '@/components/search/loading'
import { PaletteResults } from '@/components/search/palette-results'
import { useLayoutStore } from '@/stores/layout'
import { useRouter } from 'next/navigation'
import { useCallback, useEffect, useState } from 'react'

import {
	CommandDialog,
	CommandEmpty,
	CommandInput,
	CommandList
} from '@/components/ui/command'
import { Tabs } from '@/components/ui/tabs'

import {
	useFeedSearch,
	useFolderSearch,
	useTagSearch,
	useUnifiedSearch
} from '@/hooks/api'
import { useSplitLayout } from '@/hooks/ui/layout/split-layout'

import type { ArticleListResponse } from '@/types/api'
import type { CommandPaletteProps } from '@/types/layout'
import type {
	FeedSearchHit,
	FolderSearchHit,
	TagSearchHit,
	UnifiedSearchHit
} from '@/types/search'

const tabOptions: Array<{
	id: 'all' | 'feeds' | 'tags' | 'folders'
	label: string
}> = [
	{ id: 'all', label: 'All' },
	{ id: 'feeds', label: 'Feeds' },
	{ id: 'tags', label: 'Tags' },
	{ id: 'folders', label: 'Folders' }
]

export function CommandPalette({ isOpen, onClose }: CommandPaletteProps) {
	const router = useRouter()
	const [searchQuery, setSearchQuery] = useState('')
	const [debouncedSearchQuery, setDebouncedSearchQuery] = useState('')
	const [activeFilter, setActiveFilter] = useState<
		'all' | 'feeds' | 'tags' | 'folders'
	>('all')

	const { shouldShowSplitLayout } = useSplitLayout()
	const { setSelectedArticle } = useLayoutStore()

	useEffect(() => {
		const timer = setTimeout(() => {
			setDebouncedSearchQuery(searchQuery)
		}, 200)

		return () => clearTimeout(timer)
	}, [searchQuery])

	const searchParams = debouncedSearchQuery.trim()
		? { q: debouncedSearchQuery }
		: undefined

	const unifiedResponse = useUnifiedSearch(
		activeFilter === 'all' ? searchParams : undefined
	)
	const feedsResponse = useFeedSearch(
		activeFilter === 'feeds' ? searchParams : undefined
	)
	const tagsResponse = useTagSearch(
		activeFilter === 'tags' ? searchParams : undefined
	)
	const foldersResponse = useFolderSearch(
		activeFilter === 'folders' ? searchParams : undefined
	)

	const searchResponse =
		activeFilter === 'all'
			? unifiedResponse
			: activeFilter === 'feeds'
				? feedsResponse
				: activeFilter === 'tags'
					? tagsResponse
					: foldersResponse

	const searchResults: Array<{
		type: 'article' | 'feed' | 'tag' | 'folder'
		hit: ArticleListResponse | FeedSearchHit | TagSearchHit | FolderSearchHit
	}> = []

	if (activeFilter === 'all') {
		if (searchResponse.data?.data) {
			for (const unifiedHit of searchResponse.data.data as UnifiedSearchHit[]) {
				searchResults.push({
					hit: unifiedHit.data,
					type: unifiedHit.type
				})
			}
		}
	} else {
		if (searchResponse.data?.data) {
			const hits = searchResponse.data.data as
				| FeedSearchHit[]
				| TagSearchHit[]
				| FolderSearchHit[]
			for (const hit of hits) {
				searchResults.push({
					hit,
					type:
						activeFilter === 'feeds'
							? 'feed'
							: activeFilter === 'tags'
								? 'tag'
								: 'folder'
				})
			}
		}
	}

	const isLoading = searchResponse.isLoading
	const error = searchResponse.error
		? searchResponse.error instanceof Error
			? searchResponse.error.message
			: 'Search failed'
		: null

	useEffect(() => {
		if (!isOpen) {
			setSearchQuery('')
			setDebouncedSearchQuery('')
		}
	}, [isOpen])

	useEffect(() => {
		const down = (e: KeyboardEvent) => {
			if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
				e.preventDefault()
				onClose()
			}
		}

		document.addEventListener('keydown', down)
		return () => document.removeEventListener('keydown', down)
	}, [onClose])

	const handleFeedSelect = useCallback(
		(feed: FeedSearchHit) => {
			router.push(`/feeds/${feed.id}`)
			onClose()
		},
		[router, onClose]
	)

	const handleArticleSelect = useCallback(
		(article: ArticleListResponse) => {
			if (shouldShowSplitLayout) {
				setSelectedArticle(article.id)
				onClose()
			} else {
				router.push(`/articles/${article.id}`)
				onClose()
			}
		},
		[router, onClose, shouldShowSplitLayout, setSelectedArticle]
	)

	const handleTagSelect = useCallback(
		(tag: TagSearchHit) => {
			router.push(`/tags/${tag.id}`)
			onClose()
		},
		[router, onClose]
	)

	const handleFolderSelect = useCallback(
		(folder: FolderSearchHit) => {
			router.push(`/folders/${folder.id}`)
			onClose()
		},
		[router, onClose]
	)

	if (isLoading) {
		return (
			<CommandDialog
				className='bg-transparent border-0 rounded-xl min-w-xl max-sm:hidden'
				description='Search articles, feeds, tags, and folders...'
				onOpenChange={onClose}
				open={isOpen}
				shouldFilter={false}
				title='Search'
			>
				<CommandInput
					onValueChange={setSearchQuery}
					placeholder='Search articles, feeds, tags, folders...'
					value={searchQuery}
				/>
				<div className='px-2 pt-2'>
					<Tabs
						onChange={(value) => setActiveFilter(value as typeof activeFilter)}
						options={tabOptions}
						value={activeFilter}
					/>
				</div>
				<CommandList>
					<SearchLoading count={3} />
				</CommandList>
			</CommandDialog>
		)
	}

	return (
		<CommandDialog
			className='bg-transparent border-0 rounded-xl min-w-xl max-sm:hidden'
			description='Search articles, feeds, tags, and folders...'
			onOpenChange={onClose}
			open={isOpen}
			shouldFilter={false}
			title='Search'
		>
			<CommandInput
				onValueChange={setSearchQuery}
				placeholder='Search articles, feeds, tags, folders...'
				value={searchQuery}
			/>
			<div className='px-2 pt-2'>
				<Tabs
					onChange={(value) => setActiveFilter(value as typeof activeFilter)}
					options={tabOptions}
					value={activeFilter}
				/>
			</div>
			<CommandList>
				{searchQuery ? (
					<>
						{searchResults.length > 0 && (
							<PaletteResults
								onArticleSelect={handleArticleSelect}
								onFeedSelect={handleFeedSelect}
								onFolderSelect={handleFolderSelect}
								onTagSelect={handleTagSelect}
								results={searchResults}
							/>
						)}

						{searchResults.length === 0 && (
							<CommandEmpty>
								{error || 'No results found. Try different keywords.'}
							</CommandEmpty>
						)}
					</>
				) : (
					<CommandEmpty>
						Search for articles, feeds, tags, or folders...
					</CommandEmpty>
				)}
			</CommandList>
		</CommandDialog>
	)
}
