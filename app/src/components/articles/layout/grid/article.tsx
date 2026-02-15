'use client'

import {
	getImageClass,
	getPublishedAtClass,
	getSelectionClass,
	getSummaryClass,
	getTitleClass
} from '@/components/articles/layout'
import { SOURCE_LIST_PATH_KEY } from '@/components/articles/layout/virtualized-list'
import { useArticlesPaginationStore } from '@/stores/articles-pagination'
import { useLayoutStore } from '@/stores/layout'
import Image from 'next/image'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { memo, useState } from 'react'

import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Card, CardContent } from '@/components/ui/card'

import { useUserPreferences } from '@/hooks/api'
import { useSplitLayout } from '@/hooks/ui/layout'

import { ArticleListResponse } from '@/types/api'

import { formatTime } from '@/utils/article'
import { getLogoUrl } from '@/utils/logo'

function getInitials(title: string): string {
	const words = title.trim().split(/\s+/)
	if (words.length >= 2 && words[0] && words[1]) {
		return (words[0]![0]! + words[1]![0]!).toUpperCase()
	}
	return title.slice(0, 2).toUpperCase()
}

function GridArticle({ article }: { article: ArticleListResponse }) {
	const { data: preferences } = useUserPreferences()
	const { selectedArticleId, setSelectedArticle } = useLayoutStore()
	const { shouldShowSplitLayout } = useSplitLayout()
	const pathname = usePathname()
	const markArticleAsRead = useArticlesPaginationStore(
		(state) => state.markArticleAsRead
	)
	const [imageError, setImageError] = useState(false)

	const feed = article?.feeds?.[0]

	const faviconUrl = getLogoUrl(feed?.website)

	const selectionClass = getSelectionClass(article, selectedArticleId)
	const imageClass = getImageClass(article)
	const titleClass = getTitleClass(article, selectedArticleId)
	const publishedAtClass = getPublishedAtClass(article, selectedArticleId)
	const summaryClass = getSummaryClass(article, selectedArticleId)

	return (
		<Card
			className={`group overflow-hidden transition-all duration-300 ease-out py-0 gap-0 border hover:border-accent dark:hover:border-accent shadow-lg shadow-black/5 dark:shadow-white/10 hover:shadow-xl hover:shadow-black/10 dark:hover:shadow-white/20 ${selectionClass}`}
		>
			{preferences?.show_article_thumbnails &&
			article?.media_url &&
			!imageError ? (
				<div className='overflow-hidden'>
					<div className='h-48 border-b border-border/50'>
						{shouldShowSplitLayout ? (
							<div
								className='w-full h-full cursor-pointer'
								onClick={() => {
									markArticleAsRead(article.id)
									setSelectedArticle(article.id)
								}}
							>
								<Image
									alt={article?.title}
									className={`w-full h-full object-cover transition-transform duration-300 group-hover:scale-105 ${imageClass}`}
									height={192}
									onError={() => setImageError(true)}
									sizes='(max-width: 768px) 100vw, 192px'
									src={`/api/image-proxy?url=${encodeURIComponent(article?.media_url)}`}
									width={192}
								/>
							</div>
						) : (
							<Link
								href={`/articles/${article?.id}`}
								onClick={() => {
									markArticleAsRead(article.id)
									sessionStorage.setItem('scroll-to-article-id', article.id)
									sessionStorage.setItem(SOURCE_LIST_PATH_KEY, pathname)
								}}
							>
								<Image
									alt={article?.title}
									className={`w-full h-full object-cover transition-transform duration-300 group-hover:scale-105 ${imageClass}`}
									height={192}
									onError={() => setImageError(true)}
									sizes='(max-width: 768px) 100vw, 192px'
									src={`/api/image-proxy?url=${encodeURIComponent(article?.media_url)}`}
									width={192}
								/>
							</Link>
						)}
					</div>
				</div>
			) : (
				<div className='overflow-hidden'>
					<div className='w-full h-48 flex items-center justify-center bg-muted'>
						{shouldShowSplitLayout ? (
							<div
								className='w-full h-full flex items-center justify-center cursor-pointer'
								onClick={() => {
									markArticleAsRead(article.id)
									setSelectedArticle(article.id)
								}}
							>
								<span className='text-6xl font-bold text-muted-foreground'>
									{getInitials(feed?.title || '??')}
								</span>
							</div>
						) : (
							<Link
								className='w-full h-full flex items-center justify-center'
								href={`/articles/${article?.id}`}
								onClick={() => {
									markArticleAsRead(article.id)
									sessionStorage.setItem('scroll-to-article-id', article.id)
									sessionStorage.setItem(SOURCE_LIST_PATH_KEY, pathname)
								}}
							>
								<span className='text-6xl font-bold text-muted-foreground'>
									{getInitials(feed?.title || '??')}
								</span>
							</Link>
						)}
					</div>
				</div>
			)}

			<CardContent className='px-4 pb-2 pt-4'>
				<div className='flex gap-4 items-center justify-between mb-3'>
					{feed ? (
						<Link
							className='flex items-center gap-2 min-w-0 shrink group/feed-info transition-opacity'
							href={`/feeds/${feed.id}`}
						>
							{preferences?.show_feed_favicons ? (
								<Avatar className='size-5 shrink-0'>
									<AvatarImage
										alt={feed.title}
										src={faviconUrl || ''}
									/>
									<AvatarFallback className='text-[10px] font-medium bg-accent text-accent-foreground'>
										{feed.title.slice(0, 2).toUpperCase()}
									</AvatarFallback>
								</Avatar>
							) : null}
							<span className='text-xs font-medium text-foreground group-hover/feed-info:text-accent-foreground transition-colors line-clamp-1'>
								{feed.title}
							</span>
						</Link>
					) : null}
					<span className={`text-xs shrink-0 ${publishedAtClass}`}>
						{article?.published_at
							? formatTime(
									article.published_at,
									preferences?.date_format || 'relative',
									preferences?.time_format || '12h'
								)
							: null}
					</span>
				</div>

				<h3
					className='font-semibold leading-tight mb-3 h-11 transition-colors'
					onClick={() => markArticleAsRead(article.id)}
				>
					{shouldShowSplitLayout ? (
						<div
							className={`hover:underline block leading-snug text-ellipsis line-clamp-2 cursor-pointer ${titleClass}`}
							onClick={() => setSelectedArticle(article.id)}
						>
							<span className='group-hover/link:text-accent-foreground transition-colors'>
								{article?.title}
							</span>
						</div>
					) : (
						<Link
							className={`hover:underline block leading-snug text-ellipsis line-clamp-2 ${titleClass}`}
							href={`/articles/${article?.id}`}
							onClick={() => {
								sessionStorage.setItem('scroll-to-article-id', article.id)
								sessionStorage.setItem(SOURCE_LIST_PATH_KEY, pathname)
							}}
						>
							<span className='group-hover/link:text-accent-foreground transition-colors'>
								{article?.title}
							</span>
						</Link>
					)}
				</h3>

				{preferences?.show_summaries && article?.summary ? (
					<p className={`text-sm mb-3 line-clamp-2 h-10 ${summaryClass}`}>
						{article?.summary}
					</p>
				) : null}
			</CardContent>
		</Card>
	)
}

export default memo(GridArticle)
