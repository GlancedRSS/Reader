'use client'

import { useUserPreferences } from '@/hooks/api/me'

import type { ArticleResponse } from '@/types/api'

import { mapFontSizeToTailwind, mapLineHeightToTailwind } from '@/utils/content'
import { formatDuration, formatRating, formatViewCount } from '@/utils/youtube'

interface YouTubeArticleProps {
	data: ArticleResponse
}

export default function YouTubeArticle({ data }: YouTubeArticleProps) {
	const { data: userPreferences } = useUserPreferences()
	const youtubeMetadata = data.platform_metadata?.youtube

	if (!youtubeMetadata?.video_id) {
		return null
	}

	const fontSizeClass = mapFontSizeToTailwind(userPreferences?.font_size)
	const lineHeightClass = mapLineHeightToTailwind(userPreferences?.font_spacing)
	const videoId = youtubeMetadata.video_id
	const embedUrl = `https://www.youtube-nocookie.com/embed/${videoId}`

	return (
		<div className='flex flex-col'>
			<div className='aspect-video w-full overflow-hidden rounded-lg shadow-lg my-4'>
				<iframe
					allow='accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture'
					allowFullScreen
					className='h-full w-full border-0'
					src={embedUrl}
					title={data.title}
				/>
			</div>

			{youtubeMetadata.duration ||
			youtubeMetadata.views ||
			youtubeMetadata.rating ? (
				<div className='flex flex-wrap items-center gap-x-4 gap-y-2 text-sm text-muted-foreground mb-4'>
					{youtubeMetadata.duration ? (
						<span className='inline-flex items-center'>
							{formatDuration(youtubeMetadata.duration)}
						</span>
					) : null}
					{youtubeMetadata.views ? (
						<span className='inline-flex items-center'>
							{formatViewCount(youtubeMetadata.views)} views
						</span>
					) : null}
					{youtubeMetadata.rating ? (
						<span className='inline-flex items-center'>
							{formatRating(youtubeMetadata.rating)}
						</span>
					) : null}
				</div>
			) : null}

			{data.content ? (
				<div
					className={`font-reading ${fontSizeClass} ${lineHeightClass}`}
					dangerouslySetInnerHTML={{ __html: data.content }}
				/>
			) : data.summary ? (
				<div className={`font-reading ${fontSizeClass} ${lineHeightClass}`}>
					{data.summary}
				</div>
			) : null}

			<a
				className='mt-4 inline-flex items-center text-sm text-primary hover:underline'
				href={data.canonical_url}
				rel='noopener noreferrer'
				target='_blank'
			>
				Watch on YouTube →
			</a>
		</div>
	)
}
