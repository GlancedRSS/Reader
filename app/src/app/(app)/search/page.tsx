'use client'

import { Header } from '@/components'
import {
	PageResults,
	SearchBox,
	SearchEmpty,
	SearchStatus
} from '@/components/search'
import { useRouter } from 'next/navigation'
import { useCallback, useEffect, useState } from 'react'

import { ScrollArea } from '@/components/ui/scroll-area'
import { Tabs } from '@/components/ui/tabs'

import { SEARCH_TABS } from '@/constants/search'

import {
	useFeedSearch,
	useFolderSearch,
	useTagSearch,
	useUnifiedSearch
} from '@/hooks/api'
import useMetadata from '@/hooks/navigation/metadata'

import type { ArticleListResponse } from '@/types/api'
import type {
	FeedSearchHit,
	FolderSearchHit,
	SearchType,
	TagSearchHit,
	UnifiedSearchHit
} from '@/types/search'

export default function SearchPage() {
	const router = useRouter()
	const [searchQuery, setSearchQuery] = useState('')
	const [debouncedSearchQuery, setDebouncedSearchQuery] = useState('')
	const [activeTab, setActiveTab] = useState<SearchType>('all')

	useMetadata('Search | Glanced Reader')

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
		activeTab === 'all' ? searchParams : undefined
	)
	const feedsResponse = useFeedSearch(
		activeTab === 'feeds' ? searchParams : undefined
	)
	const tagsResponse = useTagSearch(
		activeTab === 'tags' ? searchParams : undefined
	)
	const foldersResponse = useFolderSearch(
		activeTab === 'folders' ? searchParams : undefined
	)

	const searchResponse =
		activeTab === 'all'
			? unifiedResponse
			: activeTab === 'feeds'
				? feedsResponse
				: activeTab === 'tags'
					? tagsResponse
					: foldersResponse

	const searchResults: Array<{
		type: 'article' | 'feed' | 'tag' | 'folder'
		hit: ArticleListResponse | FeedSearchHit | TagSearchHit | FolderSearchHit
	}> = []

	if (activeTab === 'all') {
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
						activeTab === 'feeds'
							? 'feed'
							: activeTab === 'tags'
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

	const handleFeedSelect = useCallback(
		(feed: FeedSearchHit) => router.push(`/feeds/${feed.id}`),
		[router]
	)

	const handleArticleSelect = useCallback(
		(article: ArticleListResponse) => router.push(`/articles/${article.id}`),
		[router]
	)

	const handleTagSelect = useCallback(
		(tag: TagSearchHit) => router.push(`/tags/${tag.id}`),
		[router]
	)

	const handleFolderSelect = useCallback(
		(folder: FolderSearchHit) => router.push(`/folders/${folder.id}`),
		[router]
	)

	return (
		<div className='mx-auto md:px-4 max-w-[640px]'>
			<Header title='Search' />
			<SearchBox
				autoFocus
				onChange={setSearchQuery}
				placeholder='Search articles, feeds, tags, folders...'
				value={searchQuery}
			/>

			<div className='px-4 py-2'>
				<Tabs
					onChange={(value) => setActiveTab(value as SearchType)}
					options={SEARCH_TABS}
					value={activeTab}
				/>
			</div>

			<ScrollArea className='h-[calc(100dvh-8rem-2.25rem-1.5rem-2.75rem)] md:h-[calc(100dvh-6rem-2rem-2.75rem)]'>
				<SearchStatus
					error={error}
					isLoading={isLoading}
				>
					{searchQuery ? (
						<>
							{searchResults.length > 0 && (
								<PageResults
									onArticleSelect={handleArticleSelect}
									onFeedSelect={handleFeedSelect}
									onFolderSelect={handleFolderSelect}
									onTagSelect={handleTagSelect}
									results={searchResults}
								/>
							)}

							{searchResults.length === 0 && <SearchEmpty />}
						</>
					) : (
						<SearchEmpty message='Search for articles, feeds, tags, or folders...' />
					)}
				</SearchStatus>
			</ScrollArea>
		</div>
	)
}
