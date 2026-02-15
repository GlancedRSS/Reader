'use client'

import Image from 'next/image'
import { useState } from 'react'
import { IoFolderOutline, IoPricetagOutline } from 'react-icons/io5'

import { Command, CommandGroup, CommandItem } from '@/components/ui/command'
import { Pill } from '@/components/ui/pill'

import { ArticleFeedList } from '@/types/content'
import type { ArticleListResponse } from '@/types/api'
import type {
	FeedSearchHit,
	FolderSearchHit,
	TagSearchHit
} from '@/types/search'

import { formatArticleDate } from '@/utils/article'
import { getLogoUrl } from '@/utils/logo'

function extractDomain(url: string): string {
	try {
		const domain = new URL(url).hostname
		return domain.replace('www.', '')
	} catch {
		return url
	}
}

function getFirstFeed(article: ArticleListResponse): ArticleFeedList | null {
	return article.feeds?.[0] || null
}

interface SearchResultItemProps {
	result: {
		type: 'article' | 'feed' | 'tag' | 'folder'
		hit: ArticleListResponse | FeedSearchHit | TagSearchHit | FolderSearchHit
	}
	index: number
	onArticleSelect: (article: ArticleListResponse) => void
	onFeedSelect: (feed: FeedSearchHit) => void
	onTagSelect: (tag: TagSearchHit) => void
	onFolderSelect: (folder: FolderSearchHit) => void
	logoErrors: Set<string>
	onLogoError: (id: string) => void
}

function SearchResultItem({
	result,
	index,
	onArticleSelect,
	onFeedSelect,
	onTagSelect,
	onFolderSelect,
	logoErrors,
	onLogoError
}: SearchResultItemProps) {
	const hasLogoError = (id: string) => logoErrors.has(id)

	if (result.type === 'article') {
		const article = result.hit as ArticleListResponse
		const firstFeed = getFirstFeed(article)
		const logoId = `article-${article.id}`
		const mediaUrl = article.media_url
			? `/api/image-proxy?url=${encodeURIComponent(article.media_url)}`
			: null

		const currentImage = hasLogoError(logoId) ? null : mediaUrl
		const displayValue = `${article.title} ${article.summary || ''}`

		return (
			<CommandItem
				keywords={[article.title, article.summary || ''].filter(Boolean)}
				onSelect={() => onArticleSelect(article)}
				value={displayValue}
			>
				<div className='flex items-center gap-3 w-full'>
					<div className='shrink-0'>
						{currentImage ? (
							<Image
								alt={article.title}
								className={`w-16 h-16 rounded object-cover ${article.is_read ? 'grayscale opacity-60' : ''}`}
								height={64}
								onError={() => onLogoError(logoId)}
								sizes='64px'
								src={currentImage}
								width={64}
							/>
						) : null}
					</div>

					<div className='flex-1 min-w-0'>
						<div className='flex justify-between gap-2'>
							<span
								className={`font-medium line-clamp-1 ${article?.is_read ? 'text-muted-foreground' : ''}`}
							>
								{article.title}
							</span>
							{article.read_later ? <Pill>Saved</Pill> : null}
						</div>
						{article.summary ? (
							<div className='text-sm text-muted-foreground line-clamp-1'>
								{article.summary}
							</div>
						) : null}
						<div className='flex justify-between items-center gap-2 text-xs text-muted-foreground mt-1'>
							{firstFeed?.title ? (
								<span className='line-clamp-1'>{firstFeed.title}</span>
							) : null}
							{article.published_at ? (
								<span className='line-clamp-1 min-w-24 text-right'>
									{formatArticleDate(article.published_at, {
										date_format: 'relative',
										time_format: '12h'
									})}
								</span>
							) : null}
						</div>
					</div>
				</div>
			</CommandItem>
		)
	}

	if (result.type === 'feed') {
		const feed = result.hit as FeedSearchHit
		const logoId = `feed-${feed.id}`
		const logoUrl = getLogoUrl(feed.website)
		const currentLogo = hasLogoError(logoId) ? null : logoUrl
		const displayValue = `${String(index).padStart(3, '0')}-${feed.title}`

		return (
			<CommandItem
				keywords={[feed.title]}
				onSelect={() => onFeedSelect(feed)}
				value={displayValue}
			>
				<div className='flex items-center gap-3 w-full'>
					{currentLogo ? (
						<div className='shrink-0'>
							<Image
								alt={feed.title}
								className={`w-10 h-10 rounded-full ${feed.is_active ? '' : 'grayscale opacity-60'}`}
								height={40}
								onError={() => onLogoError(logoId)}
								sizes='40px'
								src={currentLogo}
								width={40}
							/>
						</div>
					) : null}

					<div className='flex-1 min-w-0 overflow-hidden'>
						<div className='font-medium line-clamp-1'>{feed.title}</div>
						{feed.website ? (
							<div className='w-full text-xs text-muted-foreground line-clamp-1'>
								{extractDomain(feed.website)}
							</div>
						) : null}
					</div>

					{feed.unread_count > 0 ? (
						<div className='min-w-0'>
							<Pill>{feed.unread_count}</Pill>
						</div>
					) : null}
				</div>
			</CommandItem>
		)
	}

	if (result.type === 'tag') {
		const tag = result.hit as TagSearchHit
		const displayValue = `${String(index).padStart(3, '0')}-${tag.name}`

		return (
			<CommandItem
				keywords={[tag.name]}
				onSelect={() => onTagSelect(tag)}
				value={displayValue}
			>
				<div className='flex items-center gap-3 w-full'>
					<IoPricetagOutline className='mx-2 scale-150 text-foreground' />

					<div className='flex-1 min-w-0'>
						<div className='font-medium line-clamp-1'>{tag.name}</div>
						<span className='text-xs text-muted-foreground line-clamp-1'>
							{tag.article_count ?? 0} article
							{tag.article_count !== 1 && 's'}
						</span>
					</div>
				</div>
			</CommandItem>
		)
	}

	if (result.type === 'folder') {
		const folder = result.hit as FolderSearchHit
		const displayValue = `${String(index).padStart(3, '0')}-${folder.name}`

		return (
			<CommandItem
				keywords={[folder.name]}
				onSelect={() => onFolderSelect(folder)}
				value={displayValue}
			>
				<div className='flex items-center gap-3 w-full'>
					<IoFolderOutline className='mx-2 scale-150 text-foreground' />

					<div className='flex-1 min-w-0'>
						<div className='font-medium line-clamp-1'>{folder.name}</div>
						<span className='text-xs text-muted-foreground line-clamp-1'>
							Folder
						</span>
					</div>

					{folder.unread_count > 0 ? (
						<div className='min-w-0'>
							<Pill>{folder.unread_count}</Pill>
						</div>
					) : null}
				</div>
			</CommandItem>
		)
	}

	return null
}

interface PageResultsProps {
	results: Array<{
		type: 'article' | 'feed' | 'tag' | 'folder'
		hit: ArticleListResponse | FeedSearchHit | TagSearchHit | FolderSearchHit
	}>
	onArticleSelect: (article: ArticleListResponse) => void
	onFeedSelect: (feed: FeedSearchHit) => void
	onTagSelect: (tag: TagSearchHit) => void
	onFolderSelect: (folder: FolderSearchHit) => void
	title?: string
}

export function PageResults({
	results,
	onArticleSelect,
	onFeedSelect,
	onTagSelect,
	onFolderSelect
}: PageResultsProps) {
	const [logoErrors, setLogoErrors] = useState<Set<string>>(new Set())

	const handleLogoError = (id: string) => {
		setLogoErrors((prev) => new Set(prev).add(id))
	}

	if (results.length === 0) {
		return null
	}

	return (
		<Command
			className='border-none'
			style={{
				backgroundImage: 'unset'
			}}
		>
			<CommandGroup>
				{results.map((result, index) => (
					<SearchResultItem
						index={index}
						key={`${result.type}-${result.hit.id}-${index}`}
						logoErrors={logoErrors}
						onArticleSelect={onArticleSelect}
						onFeedSelect={onFeedSelect}
						onFolderSelect={onFolderSelect}
						onLogoError={handleLogoError}
						onTagSelect={onTagSelect}
						result={result}
					/>
				))}
			</CommandGroup>
		</Command>
	)
}
