'use client'

import {
	getImageClass,
	getPublishedAtClass,
	getSelectionClass,
	getSummaryClass,
	getTitleClass
} from '@/components/articles/layout'
import ListLoading from '@/components/articles/layout/list/loading'
import { SOURCE_LIST_PATH_KEY } from '@/components/articles/layout/virtualized-list'
import { useArticlesPaginationStore } from '@/stores/articles-pagination'
import { useLayoutStore } from '@/stores/layout'
import Image from 'next/image'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useEffect, useRef, useState } from 'react'

import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'

import { useUserPreferences } from '@/hooks/api'
import { useSplitLayout } from '@/hooks/ui/layout'

import { ArticleListResponse } from '@/types/api'

import { formatTime } from '@/utils/article'
import { getLogoUrl } from '@/utils/logo'

interface ListArticleProps {
	index: number
	style: React.CSSProperties
	articles: ArticleListResponse[]
	setRowHeight: (index: number, height: number) => void
}

function ListArticle({
	index,
	articles,
	style,
	setRowHeight
}: ListArticleProps) {
	const { data: preferences } = useUserPreferences()
	const { selectedArticleId, setSelectedArticle } = useLayoutStore()
	const { shouldShowSplitLayout } = useSplitLayout()
	const pathname = usePathname()
	const markArticleAsRead = useArticlesPaginationStore(
		(state) => state.markArticleAsRead
	)

	const [imageError, setImageError] = useState(false)
	const [logoError, setLogoError] = useState(false)

	const rowRef = useRef<HTMLDivElement>(null)
	const hasMeasured = useRef(false)

	const article = articles[index]

	const selectionClass = getSelectionClass(article, selectedArticleId)
	const imageClass = getImageClass(article)
	const titleClass = getTitleClass(article, selectedArticleId)
	const publishedAtClass = getPublishedAtClass(article, selectedArticleId)
	const summaryClass = getSummaryClass(article, selectedArticleId)

	useEffect(() => {
		if (rowRef.current && !hasMeasured.current && article) {
			requestAnimationFrame(() => {
				if (rowRef.current) {
					const height = rowRef.current.offsetHeight
					setRowHeight(index, height)
					hasMeasured.current = true
				}
			})
		}
	}, [index, setRowHeight, article])

	const feed = article?.feeds?.[0]
	const logoUrl = getLogoUrl(feed?.website)
	const currentLogo = logoError ? null : logoUrl

	if (!article) {
		return (
			<div
				className='mt-1.5'
				ref={rowRef}
				style={style}
			>
				{Array.from({ length: 12 }).map((_, index) => (
					<ListLoading key={index} />
				))}
			</div>
		)
	}

	return (
		<div
			className={`group transition-colors duration-300 flex items-start space-x-2 py-2 border-b last-of-type:border-b-0 px-2 ${selectionClass}`}
			ref={rowRef}
			style={style}
		>
			<div className='shrink-0'>
				{preferences?.show_article_thumbnails &&
				article.media_url &&
				!imageError ? (
					<div
						className={`relative ${preferences?.show_summaries ? 'w-16 h-16' : 'w-10 h-10'} rounded-md overflow-hidden`}
					>
						{shouldShowSplitLayout ? (
							<div
								className='w-full h-full cursor-pointer'
								onClick={() => {
									markArticleAsRead(article.id)
									setSelectedArticle(article.id)
								}}
							>
								<Image
									alt={article.title}
									className={`absolute inset-0 w-full h-full object-cover duration-300 group-hover:scale-105 ${imageClass}`}
									height={preferences?.show_summaries ? 64 : 40}
									onError={() => setImageError(true)}
									sizes={`${preferences?.show_summaries ? '64px' : '40px'}`}
									src={`/api/image-proxy?url=${encodeURIComponent(article.media_url)}`}
									width={preferences?.show_summaries ? 64 : 40}
								/>
							</div>
						) : (
							<Link
								href={`/articles/${article.id}`}
								onClick={() => {
									markArticleAsRead(article.id)
									sessionStorage.setItem('scroll-to-article-id', article.id)
									sessionStorage.setItem(SOURCE_LIST_PATH_KEY, pathname)
								}}
							>
								<Image
									alt={article.title}
									className={`absolute inset-0 w-full h-full object-cover duration-300 group-hover:scale-105 ${imageClass}`}
									height={preferences?.show_summaries ? 64 : 40}
									onError={() => setImageError(true)}
									sizes={`${preferences?.show_summaries ? '64px' : '40px'}`}
									src={`/api/image-proxy?url=${encodeURIComponent(article.media_url)}`}
									width={preferences?.show_summaries ? 64 : 40}
								/>
							</Link>
						)}
					</div>
				) : (
					<div
						className={`relative ${preferences?.show_summaries ? 'w-16 h-16' : 'w-10 h-10'} rounded-md overflow-hidden ${preferences?.show_article_thumbnails ? '' : 'hidden'}`}
					/>
				)}
			</div>

			<div className='flex-1 min-w-0'>
				<h3
					className='font-medium text-sm leading-tight mb-1 transition-colors'
					onClick={() => markArticleAsRead(article.id)}
				>
					{shouldShowSplitLayout ? (
						<div
							className={`h-5 hover:underline leading-snug line-clamp-1 group-hover/link:text-accent-foreground cursor-pointer ${titleClass}`}
							onClick={() => setSelectedArticle(article.id)}
						>
							{article.title}
						</div>
					) : (
						<Link
							className={`h-5 hover:underline leading-snug line-clamp-1 group-hover/link:text-accent-foreground ${titleClass}`}
							href={`/articles/${article.id}`}
							onClick={() => {
								sessionStorage.setItem('scroll-to-article-id', article.id)
								sessionStorage.setItem(SOURCE_LIST_PATH_KEY, pathname)
							}}
						>
							{article.title}
						</Link>
					)}
				</h3>

				{feed ? (
					<div className='flex items-center justify-between'>
						<Link
							className='min-w-0 shrink group/feed-info transition-colors flex gap-2'
							href={`/feeds/${feed.id}`}
						>
							{preferences?.show_feed_favicons ? (
								<Avatar className='size-4!'>
									<AvatarImage
										alt={feed.title}
										onError={() => {
											if (!logoError) {
												setLogoError(true)
											}
										}}
										src={currentLogo || ''}
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
						<span
							className={`text-xs text-muted-foreground shrink-0 ml-2 ${publishedAtClass}`}
						>
							{article.published_at
								? formatTime(
										article.published_at,
										preferences?.date_format || 'relative',
										preferences?.time_format || '12h'
									)
								: null}
						</span>
					</div>
				) : null}

				{preferences?.show_summaries && article.summary ? (
					<p className={`text-xs mt-1 line-clamp-1 ${summaryClass}`}>
						{article.summary}
					</p>
				) : null}
			</div>
		</div>
	)
}

export default ListArticle
