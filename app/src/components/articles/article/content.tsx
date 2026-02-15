'use client'

import HtmlRenderer from '@/components/articles/article/html-renderer'
import {
	ImageGallery,
	extractImagesFromHtml
} from '@/components/articles/article/image-gallery'
import PodcastPlayer from '@/components/articles/article/podcast-player'
import YouTubeArticle from '@/components/articles/article/youtube-article'
import Image from 'next/image'
import { useState } from 'react'

import { Skeleton } from '@/components/ui/skeleton'

import { useUserPreferences } from '@/hooks/api/me'

import type { ArticleResponse } from '@/types/api'

import { mapFontSizeToTailwind, mapLineHeightToTailwind } from '@/utils/content'

export default function ArticleContent({
	data,
	loading
}: {
	data: ArticleResponse | undefined
	loading: boolean
}) {
	const [galleryOpen, setGalleryOpen] = useState(false)
	const [selectedImageIndex, setSelectedImageIndex] = useState(0)

	const { data: userPreferences } = useUserPreferences()

	const images =
		data?.content || data?.media_url
			? extractImagesFromHtml(data.content || '', data.media_url || '')
			: []

	const handleImageClick = (src: string) => {
		if (!src) return
		const index = images.findIndex(
			(img) => img.src === src || img.src.includes(src.split('?', 1)[0] ?? '')
		)
		setSelectedImageIndex(index >= 0 ? index : 0)
		setGalleryOpen(true)
	}

	const fontSizeClass = mapFontSizeToTailwind(userPreferences?.font_size)
	const lineHeightClass = mapLineHeightToTailwind(userPreferences?.font_spacing)

	const isYouTubeVideo = data?.platform_metadata?.youtube?.video_id
	const isPodcast = data?.platform_metadata?.podcast?.audio_url

	if (loading) {
		return (
			<div className='space-y-4'>
				<div
					className='relative w-full'
					style={{ aspectRatio: '16/9' }}
				>
					<Skeleton className='absolute inset-0 rounded-xl' />
				</div>
				<Skeleton className='h-24 w-full' />
				<Skeleton className='h-20 w-5/6' />
				<Skeleton className='h-28 w-full' />
				<Skeleton className='h-16 w-4/5' />
			</div>
		)
	}

	if (isYouTubeVideo && data) {
		return <YouTubeArticle data={data} />
	}

	if (isPodcast && data) {
		return <PodcastPlayer data={data} />
	}

	const hasEmbeddedImage = Boolean(
		data?.content &&
			data?.media_url &&
			data.content.includes(data.media_url!.split('?')[0] ?? '')
	)

	const renderFeaturedImage = (articleData: ArticleResponse) => (
		<div
			className='relative cursor-pointer group'
			onClick={() => {
				if (articleData.media_url) handleImageClick(articleData.media_url)
			}}
		>
			<Image
				alt={articleData.title}
				className='rounded-xl shadow-sm mb-4 transition-opacity group-hover:opacity-80'
				height={504}
				sizes='(max-width: 768px) 100vw, 896px'
				src={`/api/image-proxy?url=${encodeURIComponent(articleData.media_url!)}`}
				style={{ height: 'auto', width: '100%' }}
				width={896}
			/>
		</div>
	)

	const renderContent = () => {
		if (data?.content?.length) {
			return (
				<>
					{data?.media_url && !hasEmbeddedImage && data
						? renderFeaturedImage(data)
						: null}
					<div className={`font-reading ${fontSizeClass} ${lineHeightClass}`}>
						<HtmlRenderer
							html={data.content || ''}
							onImageClick={handleImageClick}
						/>
					</div>
				</>
			)
		}
		return (
			<>
				{data?.media_url && data ? renderFeaturedImage(data) : null}
				<div className={`font-reading ${fontSizeClass} ${lineHeightClass}`}>
					{data?.summary || 'No content available'}
				</div>
			</>
		)
	}

	return (
		<>
			{renderContent()}
			{images.length > 0 && (
				<ImageGallery
					images={images}
					initialIndex={selectedImageIndex}
					onOpenChange={setGalleryOpen}
					open={galleryOpen}
				/>
			)}
		</>
	)
}
