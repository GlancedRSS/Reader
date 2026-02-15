'use client'

import { useRef, useState } from 'react'

import { useUserPreferences } from '@/hooks/api/me'

import type { ArticleResponse } from '@/types/api'

import { mapFontSizeToTailwind, mapLineHeightToTailwind } from '@/utils/content'

interface PodcastArticleProps {
	data: ArticleResponse
}

export default function PodcastPlayer({ data }: PodcastArticleProps) {
	const { data: userPreferences } = useUserPreferences()
	const podcastMetadata = data.platform_metadata?.podcast
	const audioRef = useRef<HTMLAudioElement>(null)

	const [isPlaying, setIsPlaying] = useState(false)
	const [currentTime, setCurrentTime] = useState(0)
	const [duration, setDuration] = useState(0)

	if (!podcastMetadata?.audio_url) {
		return null
	}

	const fontSizeClass = mapFontSizeToTailwind(userPreferences?.font_size)
	const lineHeightClass = mapLineHeightToTailwind(userPreferences?.font_spacing)

	const togglePlay = () => {
		if (audioRef.current) {
			if (isPlaying) {
				audioRef.current.pause()
			} else {
				audioRef.current.play()
			}
			setIsPlaying(!isPlaying)
		}
	}

	const handleTimeUpdate = () => {
		if (audioRef.current) {
			setCurrentTime(audioRef.current.currentTime)
		}
	}

	const handleLoadedMetadata = () => {
		if (audioRef.current) {
			setDuration(audioRef.current.duration)
		}
	}

	const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
		const time = parseFloat(e.target.value)
		if (audioRef.current) {
			audioRef.current.currentTime = time
			setCurrentTime(time)
		}
	}

	const formatTime = (time: number) => {
		if (isNaN(time)) return '0:00'
		const minutes = Math.floor(time / 60)
		const seconds = Math.floor(time % 60)
		return `${minutes}:${seconds.toString().padStart(2, '0')}`
	}

	const progress = duration > 0 ? (currentTime / duration) * 100 : 0

	return (
		<div className='flex flex-col'>
			<div className='my-4 rounded-lg border bg-muted p-4'>
				<audio
					onEnded={() => setIsPlaying(false)}
					onLoadedMetadata={handleLoadedMetadata}
					onPause={() => setIsPlaying(false)}
					onPlay={() => setIsPlaying(true)}
					onTimeUpdate={handleTimeUpdate}
					ref={audioRef}
					src={podcastMetadata.audio_url}
				/>

				<div className='flex items-center gap-4'>
					<button
						aria-label={isPlaying ? 'Pause' : 'Play'}
						className='flex h-10 w-10 items-center justify-center rounded-full bg-primary text-primary-foreground hover:bg-primary/90 transition-colors'
						onClick={togglePlay}
						type='button'
					>
						{isPlaying ? (
							<svg
								fill='currentColor'
								height='16'
								viewBox='0 0 16 16'
								width='16'
							>
								<path d='M5.5 3.5A1.5 1.5 0 0 1 7 5v6a1.5 1.5 0 0 1-3 0V5a1.5 1.5 0 0 1 1.5-1.5zm5 0A1.5 1.5 0 0 1 12 5v6a1.5 1.5 0 0 1-3 0V5a1.5 1.5 0 0 1 1.5-1.5z' />
							</svg>
						) : (
							<svg
								fill='currentColor'
								height='16'
								viewBox='0 0 16 16'
								width='16'
							>
								<path d='m11.596 8.697-6.363 3.692c-.54.313-1.233-.069-1.543-.474a1.58 1.58 0 0 1-.551-.61c-.092-.09-.145-.221-.145-.354V4.853c0-.133.053-.264.145-.354.09-.106.2-.09.456.09.606.274.274.786.382 1.543.474l6.363 3.692a.5.5 0 0 1 .551 0' />
							</svg>
						)}
					</button>

					<div className='flex-1'>
						<input
							className='w-full cursor-pointer accent-primary'
							max='100'
							min='0'
							onChange={handleSeek}
							step='0.1'
							type='range'
							value={progress}
						/>
						<div className='flex justify-between text-xs text-muted-foreground'>
							<span>{formatTime(currentTime)}</span>
							<span>{formatTime(duration)}</span>
						</div>
					</div>
				</div>
			</div>

			{data.content ? (
				<div
					className={`font-reading ${fontSizeClass} ${lineHeightClass}`}
					dangerouslySetInnerHTML={{ __html: data.content || '' }}
				/>
			) : data.summary ? (
				<div className={`font-reading ${fontSizeClass} ${lineHeightClass}`}>
					{data.summary}
				</div>
			) : null}

			{data.canonical_url ? (
				<a
					className='mt-4 inline-flex items-center text-sm text-primary hover:underline'
					href={data.canonical_url}
					rel='noopener noreferrer'
					target='_blank'
				>
					Visit original →
				</a>
			) : null}
		</div>
	)
}
