'use client'

import {
	getImageClass,
	getPublishedAtClass,
	getSelectionClass,
	getSummaryClass,
	getTitleClass
} from '@/components/articles/layout'
import MagazineLoading from '@/components/articles/layout/magazine/loading'
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

interface MagazineArticleProps {
	index: number
	style: React.CSSProperties
	articles: ArticleListResponse[]
	setRowHeight: (index: number, height: number) => void
}

function MagazineArticle({
	index,
	articles,
	style,
	setRowHeight
}: MagazineArticleProps) {
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

	const selectionClass = getSelectionClass(
		article,
		selectedArticleId,
		'magazine'
	)
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
				className='mt-3 space-y-6'
				ref={rowRef}
				style={style}
			>
				{Array.from({ length: 12 }).map((_, loadingIndex) => (
					<MagazineLoading key={loadingIndex} />
				))}
			</div>
		)
	}

	return (
		<div
			className={`group transition-colors duration-300 flex items-start space-x-4 py-2 px-2 ${selectionClass}`}
			ref={rowRef}
			style={style}
		>
			<div className='shrink-0'>
				{preferences?.show_article_thumbnails &&
				article.media_url &&
				!imageError ? (
					<div
						className={
							shouldShowSplitLayout
								? `relative w-16 ${preferences?.show_summaries ? 'h-32' : 'h-18'} rounded-lg overflow-hidden`
								: `relative w-16 ${preferences?.show_summaries ? 'h-32' : 'h-18'} sm:w-32 sm:h-24 md:w-48 md:h-32 rounded-lg overflow-hidden`
						}
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
									className={`w-full h-full object-cover transition-transform duration-200 group-hover:scale-105 ${imageClass}`}
									height={128}
									onError={() => setImageError(true)}
									sizes='(max-width: 640px) 64px, (max-width: 768px) 128px, (max-width: 1024px) 192px, 256px'
									src={`/api/image-proxy?url=${encodeURIComponent(article.media_url)}`}
									width={192}
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
									className={`w-full h-full object-cover transition-transform duration-200 group-hover:scale-105 ${imageClass}`}
									height={128}
									onError={() => setImageError(true)}
									sizes='(max-width: 640px) 64px, (max-width: 768px) 128px, (max-width: 1024px) 192px, 256px'
									src={`/api/image-proxy?url=${encodeURIComponent(article.media_url)}`}
									width={192}
								/>
							</Link>
						)}
					</div>
				) : (
					<div
						className={`relative w-16 ${preferences?.show_summaries ? 'h-32' : 'h-18'} ${shouldShowSplitLayout ? '' : 'sm:w-32 sm:h-24 md:w-48 md:h-32'} ${preferences?.show_article_thumbnails ? '' : 'hidden'} rounded-lg overflow-hidden`}
					/>
				)}
			</div>

			<div className='flex-1 min-w-0'>
				<h3
					className='font-semibold text-base lg:text-lg leading-tight max-md:mb-1 md:mb-2 transition-colors'
					onClick={() => markArticleAsRead(article.id)}
				>
					{shouldShowSplitLayout ? (
						<div
							className={`group-hover/link:text-accent-foreground hover:underline block leading-snug text-ellipsis line-clamp-2 cursor-pointer ${titleClass}`}
							onClick={() => setSelectedArticle(article.id)}
						>
							{article.title}
						</div>
					) : (
						<Link
							className={`group-hover/link:text-accent-foreground hover:underline block leading-snug text-ellipsis line-clamp-2 ${titleClass}`}
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

				{preferences?.show_summaries && article.summary ? (
					<p
						className={`max-md:mb-1 md:mb-2 text-sm text-muted-foreground leading-relaxed ${shouldShowSplitLayout ? 'line-clamp-2' : 'max-sm:line-clamp-2 max-md:line-clamp-1 md:line-clamp-2'} ${summaryClass}`}
					>
						{article.summary}
					</p>
				) : null}

				{feed ? (
					<div className='flex gap-4 justify-between'>
						<Link
							className='min-w-0 flex gap-1 shrink group/feed-info transition-colors'
							href={`/feeds/${feed.id}`}
						>
							{preferences?.show_article_thumbnails &&
							preferences?.show_feed_favicons ? (
								<Avatar variant='tiny'>
									<AvatarImage
										alt={feed.title}
										onError={() => {
											if (!logoError) {
												setLogoError(true)
											}
										}}
										src={currentLogo || ''}
									/>
									<AvatarFallback className='text-xs font-medium bg-accent text-accent-foreground'>
										{feed.title.slice(0, 2).toUpperCase()}
									</AvatarFallback>
								</Avatar>
							) : null}
							<span className='text-sm font-medium text-foreground group-hover/feed-info:text-accent-foreground transition-colors line-clamp-1'>
								{feed.title}
							</span>
						</Link>
						<span className={`text-sm shrink-0 ${publishedAtClass}`}>
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
			</div>
		</div>
	)
}

export default MagazineArticle
